from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script462c2c0e0a7d4495b243de6710518db7(Strategy):
    __script_name__ = 'NASDAQ High Morning Notion Imbal'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
        
        return md.stat.prev_close >= 20 and md.stat.avol >= 1000000

    def on_start(self, md, order, service, account):
        self.imbalance_started = 0
        self.tradeok = 0
        self.traded = 0
        self.exitok = 0
        
        self.quantity = md.nasdaq_imb.imbalance_quantity
        self.notionalVal = self.quantity * md.stat.prev_close
        
        service.add_time_trigger(service.time(9, 28, 1))                   # NASDAQ posts imbalance info
        service.add_time_trigger(service.time(9, 30, 5))

    def on_nasdaq_imbalance(self, event, md, order, service, account):
        pass
            
    def on_trade(self, event, md, order, service, account):
        if self.tradeok == 1 and self.traded == 0:
            print(self.notionalVal)
            if self.notionalVal <= -1000000 or md.nasdaq_imb.imbalance_quantity >= 0.5*(md.stat.avol):
                order.algo_buy(self.symbol,algorithm='add_trade',intent = 'init',order_quantity = 100)
                self.traded = 1
            if self.exitok == 1 and account[self.symbol].position.shares != 0:
                order.algo_sell(self.symbol, algorithm='market', intent='exit')
                           
    def on_timer(self, event, md, order, service, account):
        if service.system_time >= service.time(9, 28) and service.system_time <= service.time(9, 28, 5):
            self.imbalance_started = 1
            self.quantity = md.nasdaq_imb.imbalance_quantity
            self.notionalVal = self.quantity * md.L1.last

        if service.system_time >= service.time(9, 28, 6) and service.system_time <= service.time(9, 29, 59):
            self.tradeok = 1

        if service.system_time >= service.time(9, 30) and service.system_time <= service.time(9, 30, 10):
            self.exitok = 1
