from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scriptc3226547e484418ebe90c5ab4adaaaf7(Strategy):
    __script_name__ = 'volume alert'

    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        # Eliminate mickey mouse stocks
        
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 10 and md.stat.avol > 1000000
    
    def on_start(self, md, order, service, account):
        
        service.add_time_trigger(service.time(9, 31))
        
        self.initVol = 0
        self.initCalculated = 0
        self.alerted = 0
    
    def on_timer(self, event, md, order, service, account): 
        self.initVol = md.L1.core_acc_volume
        self.initCalculated = 1
        
    def on_trade(self, event, md, order, service, account):
        if(self.initCalculated == 1 and self.alerted == 0):
            if(md.L1.minute_volume >= 0.25*self.initVol):
                _alertList = [('Price', md.L1.last), ('Message', 'Stock is trading >25% of its opening vol')]
                service.alert( md.symbol, 'b7069e93-0dc3-40e2-8224-c6d395088d39', _alertList )
                self.alerted = 1
