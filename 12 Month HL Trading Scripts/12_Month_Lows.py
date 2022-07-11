from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script3df63fa235ba456aab61c869a95442c6(Strategy):
    __script_name__ = '12_Month_Low'

    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 15 and md.stat.avol > 1000000
            
    def on_start(self, md, order, service, account):
        bars = md.bar.daily(start = -264, end = -1)
        bars_low = bars.low
        if(len(bars.low) >= 150):                                             
            low = min(bars.low)
            self.qualified = ((md.stat.prev_close - low)/low)              
            self.low = low                                         
        else:
            self.qualified = 0
            
        self.traded = 0                                                        # Whether a stock has been traded or not
        self.time_ok = 0
                
        service.add_time_trigger(service.time(9, 45))
        service.add_time_trigger(service.time(12, 50))
                
    # Alert at 2%
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 0.025 and self.time_ok == 1):
                        
            if(md.L1.last <= self.low and self.traded == 0):                                   
                num_shares = round((200/(1.03*(md.L1.last) - md.L1.last)))                  
                order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='init', order_quantity=num_shares)
                self.traded = 1                                                                
                                                                                                    
        if(account[self.symbol].position.shares != 0):                                            
            if(md.L1.last > 1.03*(account[self.symbol].position.entry_price)):
                order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')
                
    # Exit 
    
    def on_timer(self, event, md, order, service, account):
        if(service.system_time >= service.time(9, 45) and service.system_time <= service.time(12,50)):
            self.time_ok = 1
        else:
            self.time_ok = 0
            order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')
        
