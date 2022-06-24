from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script7069f6af08d2470b966bea08b69990be(Strategy):
    __script_name__ = '12_month_lows'
    
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
        
        bars = md.bar.daily(start = -264, end = -1)
        bars_low = bars.low
        if(len(bars.low) >= 250):
            low = min(bars.low)
            # Console Print for backtest
            # print('The 12-month low is ' + str(low))
            # print('---------------------------------')
            
            self.qualified = ((md.stat.prev_close - low)/low)                                      # Amount stock is trading above low
            self.low = low
            print(self.low)
            print(self.qualified)
        else:
            self.qualified = 0
            
        self.traded = 0
        self.alerted_at_2 = 0
        
        service.add_time_trigger(service.time(15, 30))
            
    # alert at 2% and 5 days before was new low
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 0.025):                  # Must be new position and trading 4% above low
                                                                                                    # on start of trade day
            if(md.L1.last <= 1.02*self.low and md.L1.last > self.low and self.alerted_at_2 == 0):   # Stock has broken 2% barrier and alert hasn't fired
                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' has reached 2% of 12 Month Low of ' + str(self.low))]
                service.alert( md.symbol, 'cf5a34c1-b6e5-4017-a316-cc652da9460f', _alertList )
                self.alerted_at_2 = 1
                        
            if(md.L1.last <= self.low and self.traded == 0):                                        # Upon making a new low, short
                _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month Low, Shorted ' + str(self.symbol))]
                service.alert( md.symbol, '2785af4f-d521-4d26-b826-50c19f40e6cc', _alertList )
                num_shares = round((1000/(md.L1.last*0.05)))                                        # Equal risk for all stocks
                                                                                                    # 1000 dollar risk given 5% stop
                order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='init', order_quantity=num_shares)
                self.traded = 1                                                                     # Prevents auto shorting if trader decides to
                                                                                                    # manually exit
            
            if(account[self.symbol].position.shares != 0):
                if(md.L1.last > 1.05*(account[self.symbol].position.entry_price)):
                    order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')
            
    # Exit at market close
    def on_timer(self, event, md, order, service, account):
        if(account[self.symbol].position.shares != 0):
            order.algo_buy(self.symbol, algorithm='market', intent='exit')

    # Scalp/stop - For testing, going to use exit at market close

        # Scalp after 3% profit or stop out after 3% loss
        # if(account[self.symbol].position.shares != 0):
            # if(md.L1.last > 1.03*(account[self.symbol].position.entry_price) or                    # Stopped out
              # md.L1.last < 0.97*(account[self.symbol].position.entry_price)):                      # Scalp
                # order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')
           
            
            #----------------------- Sell Init-----------------------
            # trade_data = {}
            # orderShares = abs(<shares>)
            # orderPrice = 0.0
            # VoodooGuid = '{'8fdee8fe-b772-46bd-b411-5544f7a0d917'  #Sell Market ARCA}'
            # order.algo_sell( md.symbol, voodooGuid, 'init', order_quantity=orderShares, price=orderPrice, allow_multiple_pending=False, user_key=None, collect=trade_data )

            #----------------------- Buy Exit-----------------------
            # trade_data = {}
            # orderPrice = 0.0
            # voodooGuid = '{'2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d'  #Buy Market ARCA}'
            # order.algo_buy( md.symbol, voodooGuid, 'exit', price=orderPrice, allow_multiple_pending=False, user_key=None, collect=trade_data )
            
