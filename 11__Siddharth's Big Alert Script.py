from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scriptb25d541998424e6fa57d46167944d5fd(Strategy):
    __script_name__ = 'Big Alert Script_SI'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
    
    # Includes only stocks in the S&P500 with an average volume of >= 1mil
    
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid), symbol)
        
        return SP500 and md.stat.avol >= 1000000

    def on_start(self, md, order, service, account):
        
    # 12 Month Highs/Lows Alerts
        
        yrBars = md.bar.daily(start = -264, end = -1)
        
        if(len(yrBars.low) >= 200):
            low = min(yrBars.low)           # 12 Month Low
            high = max(yrBars.high)         # 12 Month High
        
            self.high = high
            self.low = low
            
            self.high_qualified = ((high - md.stat.prev_close)/high)
            self.low_qualified = ((md.stat.prev_close - low)/low)
            
            self.high_2_alerted = 0
            self.low_2_alerted = 0
            self.new_high_alerted = 0
            self.new_low_alerted = 0
            
    # Gap Alerts
    
    # This system won't pull data reliably if you try and instantiate open and close in the on_start method. Easiest solution was to use a time trigger,
    # but we can look for another way.
    
        service.add_time_trigger(service.time(9, 31), repeat_interval=service.time_interval(1, 0, 0, 0))
    
        self.open = 0
        self.close = 0
        
        self.gap_empty = 0              # Gap metrics
        self.gap_fill = 0
        self.gap_size = 0
        self.gap_distance = 0
        self.gap_amt_filled = 0
        
        self.gap_up = 0                 # Gap up or down
        self.gap_down = 0
        
        self.gap_qualified = 0
        
    # High Volume Alert
    
        self.initVol = 0
        self.initVolCalculated = 0
        self.highVolAlerted = 0
    
    def on_timer(self, event, md, order, service, account):
    
        # Calculate Gaps
        
        self.open = md.L1.open
        self.close = md.stat.prev_close
        self.qualified = 100*((md.L1.open - md.stat.prev_close)/(md.stat.prev_close))
        
        if(self.qualified >= 3):
            self.gap_up = 1
            self.gap_down = 0
            self.fill = md.stat.prev_close
            self.empty = md.L1.open
            self.gap_size = abs(self.fill - self.empty)
            
            if(md.L1.last > self.empty):
                self.distance = abs(md.L1.last - self.empty)

                _alertList = [('Price', md.L1.last), ('Message', 'Trading $' + str(self.distance) + ' Away From Gap Up at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
                
            elif(md.L1.last < self.empty):
                self.amt_fill = abs(100*((md.L1.last - self.empty)/self.gap_size))
                
                if(self.amt_fill >= 99):
                    _alertList = [('Price', md.L1.last), ('Message', 'Gap Up Filled at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                    service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
                
                else:
                    _alertList = [('Price', md.L1.last), ('Message', 'Filled ' + str(round(self.amt_fill,2)) + '% of Gap Up at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                    service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
                                        
        elif(self.qualified <= -3):
            self.gap_down = 1
            self.gap_up = 0
            self.fill = md.stat.prev_close
            self.empty = md.L1.open
            self.gap_size = abs(self.fill - self.empty)
            
            if(md.L1.last < self.empty):
                self.distance = abs(md.L1.last - self.empty)

                _alertList = [('Price', md.L1.last), ('Message', 'Trading $' + str(self.distance) + ' Away From Gap Down at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
                
            elif(md.L1.last > self.empty):
                self.amt_fill = abs(100*((md.L1.last - self.empty)/self.gap_size))
                
                if(self.amt_fill >= 99):
                    _alertList = [('Price', md.L1.last), ('Message', 'Gap Down Filled at ' + str(service.system_time))]
                    service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
                    
                else:
                    _alertList = [('Price', md.L1.last), ('Message', 'Filled ' + str(round(self.amt_fill,2)) + '% of Gap Down at ' + service.time_to_string(service.system_time,format="%H:%M:%S"))]
                    service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
        
    # Calculate Initial Volume
    
        if(self.initVolCalculated == 0):
            self.initVol =md.L1.core_acc_volume
    
    def on_trade(self, event, md, order, service, account):
        
    # On trade checks for 12 Month Highs/Lows
    
        if(hasattr(self,'high_qualified')):
            if(self.high_qualified >= 0.025 and self.high_qualified <= 0.075):                              # Trading between 2.5 and 7.5% of 12 Month High
            
                if(md.L1.last < self.high and md.L1.last >= 0.98*self.high and self.high_2_alerted == 0):  # 2% of High Alert
                
                    _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' 2% of 12 Month High of ' + str(self.high)+ ', Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                    service.alert( md.symbol, '1fadb38a-4a12-4891-adee-d35fcca5e2be', _alertList )
                    self.high_2_alerted = 1
                            
                if(md.L1.last > self.high and self.new_high_alerted == 0):                                  # New High Alert
                    
                    _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month High, Time:' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                    service.alert( md.symbol, '44a652e4-c113-4512-8ce9-76e3cff8af6e', _alertList )
                    self.new_high_alerted = 1

        if(hasattr(self,'low_qualified')):
            if(self.low_qualified <= 0.025 and self.low_qualified >= 0.075):
                
                if(md.L1.last <= 1.02*self.low and md.L1.last > self.low and self.low_2_alerted == 0):     # 2% of Low Alert
                
                    _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' 2% of 12 Month Low of ' + str(self.low) + ', Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                    service.alert( md.symbol, 'cf5a34c1-b6e5-4017-a316-cc652da9460f', _alertList )
                    self.low_2_alerted = 1                                                 
                            
                if(md.L1.last <= self.low and self.traded == 0):                                            # New Low Alert
                
                    _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month Low, Time: ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                    service.alert( md.symbol, '2785af4f-d521-4d26-b826-50c19f40e6cc', _alertList )
                    self.new_low_alerted = 1
                
    # On trade checks for abnormally high volume
    
        if(hasattr(self,'initVol')):
            if(self.initVolCalculated == 1 and self.highVolAlerted == 0):
                if(md.L1.minute_volume >= 0.25*self.initVol):
                    _alertList = [('Price', md.L1.last), ('Message', 'Stock Trading >25% of Open Vol at ' + service.time_to_string(service.system_time, format='%H:%M:%S'))]
                    service.alert( md.symbol, 'b7069e93-0dc3-40e2-8224-c6d395088d39', _alertList )
                    self.alerted = 1
                
