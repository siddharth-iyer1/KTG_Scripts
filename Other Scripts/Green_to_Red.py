from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scriptb41cecea72644d8280e8196320bdd0d8(Strategy):
    __script_name__ = 'Earnings_Gap_Up'

    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        # Eliminate mickey mouse stocks
        
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 10 and md.stat.avol > 1000000
            
    def on_start(self, md, order, service, account):
        
        service.add_time_trigger(service.time(9, 40))
        service.add_time_trigger(service.time(12, 50))                                  # Cover at 3:30 EST
        
        self.open = 0           # Open Price
        self.qualified = 0
        
        self.traded = 0         # Has it been traded or not
        self.alerted = 0        # Has it been alerted
        self.stop_price = 0     # Place stops
        
    
    def on_timer(self, event, md, order, service, account):
        self.open = md.L1.open
        self.qualified = 100*((md.L1.open - md.stat.prev_close)/(md.stat.prev_close))
        if(self.qualified >= 2):
            print('Symbol: ' + str(self.symbol))
            print('Open: ' + str(self.open))
            print('Gap up percentage: ' + str(self.qualified))
        
        if(account[self.symbol].position.shares != 0):
            order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')    
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 4):       # Gap up at least 4%
            
            if(md.L1.last <= (1.01*(md.stat.prev_close)) and md.L1.last >= md.stat.prev_close):
                
                # Alert - Approached Bottom of Gap
                _alertList = [('Price', md.L1.last), ('Message', 'Stock has reached 1% of bottom of gap')]
                service.alert( md.symbol, 'aa7631f9-0c12-4d62-b808-686bcfc3438b', _alertList )
                self.alerted = 1
                
            elif(md.L1.last <= md.stat.prev_close and self.alerted == 1 and self.traded == 0):
                self.stop_price = md.L1.daily_high + 0.25
                num_shares = round((200/(self.stop_price)))                             # $200 Risk
                
                # Green to Red
                _alertList = [('Price', md.L1.last), ('Message', 'Stock has breached bottom of gap')]
                service.alert( md.symbol, 'b6e7be7f-0f14-4401-aa50-41ac4e54b6af', _alertList )
                
                order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='init', order_quantity=100)
                self.traded = 1
                
        elif(account[self.symbol].position.shares != 0):
            if(md.L1.last >= self.stop_price):
                order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='exit')
                
