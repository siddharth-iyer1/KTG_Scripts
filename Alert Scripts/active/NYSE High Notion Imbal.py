from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Scriptafe758ada81f4ca7803c233686395d03(Strategy):
    __script_name__ = 'imbalance attempt'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
    
    # Includes only stocks in the S&P500 with an average volume of >= 1mil
    
        SP500guid = '9a802d98-a2d7-4326-af64-cea18f8b5d61'
        SP500 = service.symbol_list.in_list(service.symbol_list.get_handle(SP500guid), symbol)
        
        return SP500 and md.stat.avol >= 1000000

    def on_start(self, md, order, service, account):
        self.notionalVal = 0
        self.numFlips = 0
        
        service.add_time_trigger(service.time(15, 59, 10))
        
    def on_nyse_imbalance(self, event, md, order, service, account):
        if(event.type == 'C'):
            self.notionalVal = md.nyse_imb.imbalance_quantity * md.L1.last
            
            if(self.notionalVal >= 300000000 or self.notionalVal <= -300000000):
                print(str(md.symbol) + ', ' + str(self.notionalVal))
            
                # IMBAL NOTION
                _alertList = [('Notional Value', self.notionalVal)]
                service.alert( md.symbol, '396f9822-0544-4a31-82cf-b7d679b26542', _alertList )
                
                if(self.notionalVal >= 300000000):
                    self.numFlips = md.nyse_imb.flip_count
                    if(self.numFlips == 0):
                        order.algo_buy(self.symbol, algorithm='market', intent='init', order_quantity=100)
                elif(self.notionalVal <= 300000000):
                    self.numFlips = md.nyse_imb.flip_count
                    if(self.numFlips == 0):
                        order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=100)
                    
    def on_timer(self, event, md, order, service, account):
        if(account[self.symbol].position.shares < 0):
            order.algo_buy(self.symbol, algorithm='market', intent='exit')
        elif(account[self.symbol].position.shares > 0):
            order.algo_sell(self.symbol, algorithm='market', intent='exit')
