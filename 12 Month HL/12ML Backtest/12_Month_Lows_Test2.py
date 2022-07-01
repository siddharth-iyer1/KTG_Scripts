from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scripte3cacb6819a347a9af9252bb8c0a8e6b(Strategy):
    __script_name__ = '12_month_lows'
    
    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 20 and md.stat.avol > 1000000
            
    def on_start(self, md, order, service, account):
        bars = md.bar.daily(start = -264, end = -1)
        bars_low = bars.low
        if(len(bars.low) >= 250):                                              # Need at least 250 days of bar data
            low = min(bars.low)
            self.qualified = ((md.stat.prev_close - low)/low)                  # Amount stock is trading above low
            self.low = low                                                     # 12 Month Low   
        else:
            self.qualified = 0
            
        self.traded = 0                                                        # Whether a stock has been traded or not
        self.alerted_at_2 = 0                                                  # Whether a stock has alerted at 2% or not
        
        # Data Collection
        self.abs_low = 0
        self.abs_low_time = 0
        self.entry_data = {}
        self.exit_data = {}
        
        service.add_time_trigger(service.time(12, 50))                         # Cover at 3:30 EST
            
    # Alert at 2%
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 0.025):                  # Must be new position and trading >2.5% above low
                                                                                                    # on start of trade day
            if(md.L1.last <= 1.02*self.low and md.L1.last > self.low and self.alerted_at_2 == 0):   # Stock has broken 2% barrier and alert hasn't fired
                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' 2% of 12 Month Low of ' + str(self.low) + ', Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                service.alert( md.symbol, 'cf5a34c1-b6e5-4017-a316-cc652da9460f', _alertList )
                self.alerted_at_2 = 1                                                               # Stock has alerted
                        
            if(md.L1.last <= self.low and self.traded == 0):                                        # Upon making a new low, short
                _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month Low, Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                service.alert( md.symbol, '2785af4f-d521-4d26-b826-50c19f40e6cc', _alertList )
                num_shares = round((200/(1.03*(md.L1.last) - md.L1.last)))                          # Equal risk for all stocks
                                                                                                    # 200 dollar risk given 3% stop
                
                self.entry_data['% ATR'] = 100*((md.L1.daily_high - md.L1.last)/md.stat.atr)        # Collect data on % ATR at entry
                self.entry_data['Entry Time'] = service.time_to_string(service.system_time, format='%H:%M:%S')
                self.abs_low = md.L1.last
                self.abs_low_time = service.time_to_string(service.system_time, format='%H:%M:%S')
                
                order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='init', order_quantity=num_shares, collect=self.entry_data)
                self.new_low = md.L1.last
                self.traded = 1                                                                     # Stock has been traded
                                                                                                    # Prevents auto shorting if trader decides to
                                                                                                    # manually exit
                                                                                                    
        if(account[self.symbol].position.shares != 0):                                              # Stop at 2% above entry
            if(md.L1.last > 1.02*(account[self.symbol].position.entry_price)):
                self.exit_data['Low of Day'] = self.abs_low
                self.exit_data['Time of Low of Day'] = self.abs_low_time
                order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit', collect=self.exit_data)


            elif(md.L1.last < self.abs_low):
                self.abs_low = md.L1.last
                self.abs_low_time = service.time_to_string(service.system_time, format='%H:%M:%S')

            
    # Exit at 3:30 EST
    
    def on_timer(self, event, md, order, service, account):
        if(account[self.symbol].position.shares != 0):
            self.exit_data['Low of Day'] = self.abs_low
            self.exit_data['Time of Low of Day'] = self.abs_low_time
            order.algo_buy(self.symbol, algorithm='market', intent='exit', collect=self.exit_data)
