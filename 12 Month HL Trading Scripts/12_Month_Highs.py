from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scripta7015fc8d54749e29af05c6985daa308(Strategy):
    __script_name__ = '12_Month_High'
    
    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 20 and md.stat.avol > 1000000
        
    # @classmethod
    # def backtesting_extra_symbols(cls, symbol, md, service, account):
    #     return ['SPY']
            
    def on_start(self, md, order, service, account):
        # print(md.symbol)
        # 
        
        bars = md.bar.daily(start = -264, end = -1)
        bars_low = bars.low
        if(len(bars.low) >= 250):
            high = max(bars.high)
            # Console Print for backtest
            # print('The 12-month low is ' + str(low))
            # print('---------------------------------')
            
            self.qualified = ((high - md.stat.prev_close)/high)                                     # Amount stock is trading away from high
            self.high = high
            print(self.high)
            print(self.qualified)
        else:
            self.qualified = 0
            
        self.traded = 0
        self.alerted_at_2 = 0
        
        service.add_time_trigger(service.time(15, 30))
            
    # alert at 2% and 5 days before was new low
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 0.025):                  # Must be new position and trading at least 2.5% below high
                                                                                                    # on start of trade day
            if(md.L1.last < self.high and md.L1.last >= 0.98*self.high and self.alerted_at_2 == 0):  # Stock has broken 2% barrier and alert hasn't fired
                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' 2% of 12 Month High of ' + str(self.high)+ ', Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                service.alert( md.symbol, '1fadb38a-4a12-4891-adee-d35fcca5e2be', _alertList )
                self.alerted_at_2 = 1
                        
            if(md.L1.last > self.high and self.traded == 0):                                        # Upon making a new low, short
                _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month High, Time:' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                service.alert( md.symbol, '44a652e4-c113-4512-8ce9-76e3cff8af6e', _alertList )
                num_shares = round((200/(md.L1.last*0.03)))                                         # Equal risk for all stocks
                                                                                                    # 200 dollar risk given 3% stop
                order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='init', order_quantity=num_shares)
                self.traded = 1                                                                     # Prevents auto buying if trader decides to
                                                                                                    # manually exit
            
            if(account[self.symbol].position.shares != 0):
                if(md.L1.last > 0.97*(account[self.symbol].position.entry_price)):
                    order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='exit')
            
    # Exit at market close
    def on_timer(self, event, md, order, service, account):
        if(account[self.symbol].position.shares != 0):
            order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='exit')
