from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script4101967b4202446ba7fdeda3a1227823(Strategy):
    __script_name__ = 'buy on gap up'
    
    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        # Eliminate mickey mouse stocks
        
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 10 and md.stat.avol > 1000000
            
    def on_start(self, md, order, service, account):
        
        service.add_time_trigger(service.time(9, 40), repeat_interval=service.time_interval(1, 0, 0, 0))
        
        self.open = 0           # Open Price
        self.close = 0
        
        self.empty = 0          # Enter the gap
        self.fill = 0           # Filled the gap
        self.gap_size = 0
        self.distance = 0
        self.amt_fill = 0
        
        self.gap_up = 0         # Is up or down
        self.gap_down = 0
        
        self.qualified = 0
        
        self.alerted1 = 0       # Has it been alerted        
    
    def on_timer(self, event, md, order, service, account):
        self.open = md.L1.open
        self.close = md.stat.prev_close
        self.qualified = 100*((md.L1.open - md.stat.prev_close)/(md.stat.prev_close))
        
        if(self.qualified >= 4):
            self.gap_up = 1
            self.gap_down = 0
            self.fill = md.stat.prev_close
            self.empty = md.L1.open
            self.gap_size = abs(self.fill - self.empty)
            
            if(md.L1.last > self.empty):
                self.distance = abs(md.L1.last - self.empty)

                _alertList = [('Price', md.L1.last), ('Message', 'Trading $' + str(self.distance) + ' away from gap up at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
                
            elif(md.L1.last < self.empty):
                self.amt_fill = abs(100*((md.L1.last - self.empty)/self.gap_size))
                
                if(self.amt_fill >= 99):
                    _alertList = [('Price', md.L1.last), ('Message', 'Gap Up Filled' + str(service.system_time))]
                    service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
                
                else:
                    _alertList = [('Price', md.L1.last), ('Message', 'Filled ' + str(round(self.amt_fill,2)) + '% of gap up at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                    service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
                                        
        elif(self.qualified <= -4):
            self.gap_down = 1
            self.gap_up = 0
            self.fill = md.stat.prev_close
            self.empty = md.L1.open
            self.gap_size = abs(self.fill - self.empty)
            
            if(md.L1.last < self.empty):
                self.distance = abs(md.L1.last - self.empty)

                _alertList = [('Price', md.L1.last), ('Message', 'Trading $' + str(self.distance) + ' away from gap up/down at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
                
            elif(md.L1.last > self.empty):
                self.amt_fill = abs(100*((md.L1.last - self.empty)/self.gap_size))
                
                if(self.amt_fill >= 99):
                    _alertList = [('Price', md.L1.last), ('Message', 'Gap Down Filled' + str(service.system_time))]
                    service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
                    
                else:
                    _alertList = [('Price', md.L1.last), ('Message', 'Filled ' + str(round(self.amt_fill,2)) + '% of gap up/down at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                    service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
                    





############################################ ALERT TEMPLATES ##################################################################
            # GAP DISTANCE
            #_alertList = [('Price', md.L1.last), ('Message', 'Stock is trading $__ from gap up/down')]
            #service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
            # GAP FILL
            #_alertList = [('Price', md.L1.last), ('Message', 'Stock has filled _% of gap up/down')]
            #service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
            # GAP FILLED
            #_alertList = [('Price', md.L1.last), ('Message', 'Stocks Gap Filled')]
            #service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
