from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script6165d698151b45c98eb81829b5c9ffa4(Strategy):

    __script_name__ = 'Gap'

    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid),symbol)

        return SP500 and md.stat.prev_close > 20 and md.stat.avol > 1000000
        
    def on_start(self, md, order, service, account):
        # Determine Gap
        self.closes = md.bar.daily(start=-20, end=-1).close
        self.opens = md.bar.daily(start=-19, end=0).open
        
        self.diffs = []
        self.gap_index = 0
        
        self.max_up = 0
        self.max_down = 0
        self.gap_up = 0
        self.gap_down = 0
        
        self.exists = 0
        self.qualified = 0
        
        self.alerted = 0
        self.traded = 0
        
        if(len(self.closes) == 19):
            for i in range(len(self.closes)):
                dif = self.opens[i] - self.closes[i]        # Next Day Open - Prev Day Close
                self.diffs.append(dif)
                self.max_up = max(self.diffs)
                self.max_down = min(self.diffs)
        
        # To double check bar data
        
        # print(self.diffs)
        # print(len(self.diffs))
        # print(self.diffs[-1])
        
        # Check gap calcs
        
        # print(max_up)
        # print(max_down)
        # print(md.stat.atr)
        
        # Determine gap existence
        
        gap_up = self.max_up >= (2*(md.stat.atr))
        gap_down = self.max_down <= (-2*(md.stat.atr))
                
        if(gap_up == True or gap_down == True):
            # Exists
            if(gap_up == True and gap_down == False):
                self.exists = 1
                self.gap_up = 1
                self.gap_index = self.diffs.index(self.max_up)
                
            elif(gap_down == True and gap_up == False):
                self.exists = 1
                self.gap_down = 1
                self.gap_index = self.diffs.index(self.max_down)
                
            elif(gap_up == True and gap_down == True):          # Edge case, if both true, we can find whichever is more recent and trade that
                pass
        
        # Check gap identification
        
        # print(self.exists)
        # print(self.gap_up)
        # print(self.gap_down)
        # print(gap_index)
        
        # Ensure stock is not trading inside gap
        
        if(self.exists == True):
            if(self.gap_up == True):
                if(md.stat.prev_close > self.opens[self.gap_index]):
                    self.qualified = 1
                    
            elif(self.gap_down == True):
                if(md.stat.prev_close < self.opens[self.gap_index]):
                    self.qualified = 1
                    
        # print(self.opens[gap_index])
        # print(self.closes[gap_index])
        # print(self.qualified)
        pass
        
    def on_trade(self, event, md, order, service, account):
        # Check for break into 2% of gap, alert
        if(self.qualified == 1 and self.gap_up == 1 and self.alerted == 0 and self.traded == 0):       # Gap Up
            if(md.L1.last <= 1.02*(self.opens[self.gap_index])):
                
                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' has reached 2% of Gap Up')]
                service.alert( md.symbol, 'aa7631f9-0c12-4d62-b808-686bcfc3438b', _alertList )
            
                self.alerted = 1

        elif(self.qualified == 1 and self.gap_down == 1 and self.alerted == 0 and self.traded == 0):     # Gap Down
            if(md.L1.last >= 0.98*(self.opens[self.gap_index])):

                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' has reached 2% of Gap Down')]
                service.alert( md.symbol, 'aa7631f9-0c12-4d62-b808-686bcfc3438b', _alertList )
                
                self.alerted = 1
            
        # Alerted already, Check for break into gap, order init
        elif(self.qualified == 1 and self.gap_up == 1 and self.alerted == 1 and self.traded == 0):
            if(md.L1.last <= self.opens[self.gap_index]):
                order.algo_sell(self.symbol, algorithm='8fdee8fe-b772-46bd-b411-5544f7a0d917', intent='init', order_quantity=100)
                
                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' has entered Gap Up. Shorted stock.')]
                service.alert( md.symbol, 'b6e7be7f-0f14-4401-aa50-41ac4e54b6af', _alertList )
                
                self.traded = 1
                
        elif(self.qualified == 1 and self.gap_down == 1 and self.alerted == 1 and self.traded == 0):
            if(md.L1.last >= self.opens[self.gap_index]):
                order.algo_buy(self.symbol, algorithm='2b4fdc55-ff01-416e-a5ea-e1f1d4524c7d', intent='init', order_quantity=100)

                _alertList = [('Price', md.L1.last), ('Message', str(self.symbol) + ' has entered Gap Down. Bought stock.')]
                service.alert( md.symbol, 'b6e7be7f-0f14-4401-aa50-41ac4e54b6af', _alertList )
                
                self.traded = 1
                









### Alerts:

            # Approached 2% of Gap
            # _alertList = [('Price', md.L1.last), ('Message', 'Stock has reached 2% of 1 Month Gap')]
            # service.alert( md.symbol, 'aa7631f9-0c12-4d62-b808-686bcfc3438b', _alertList )
            # Breached Gap
            # _alertList = [('Price', md.L1.last), ('Message', 'Stock has entered the gap')]
            # service.alert( md.symbol, 'b6e7be7f-0f14-4401-aa50-41ac4e54b6af', _alertList )


