from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scripta758ca5b7afe4a15a262b56701c43367(Strategy):
    __script_name__ = 'Inside Day'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
        
        return md.stat.avol >= 800000

    def on_start(self, md, order, service, account):
        self.data = md.bar.daily(start = -2, end = 0)
        
        if len(self.data.high) > 1:
            self.qualified = 1
            self.high_before = self.data.close[0]
            self.low_before = self.data.open[0]
            
            self.high_inside = max(self.data.open[-1], self.data.close[-1])
            self.low_inside = min(self.data.open[-1], self.data.close[-1])
            
            print(self.symbol, self.high_before)
            print(self.symbol, self.low_before)
            print(self.symbol, self.high_inside)
            print(self.symbol, self.low_inside)
        else:
            self.qualified = 0
        
        service.add_time_trigger(service.time(9, 30, 5))
        
        
    def on_timer(self, event, md, order, service, account):
        if self.qualified == 1:
            if(self.high_before - self.low_before >= ((1.2)*md.stat.atr)):
            # Check inside day
                if self.high_inside < self.high_before and self.low_inside > self.low_before:
                     # INSIDE DAY
                    _alertList = [('Price', md.L1.last), ('Message', 'Stock had an inside day yday')]
                    service.alert( md.symbol, 'b64fc11b-a850-45dd-aea1-21ca84babe65', _alertList )
    
