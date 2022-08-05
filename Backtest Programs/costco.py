from cloudquant.interfaces import Strategy, Event
import ktgfunc

class Gr8Script8a2a98c4bd53409aa6f67c77a230cb8d(Strategy):
    __script_name__ = 'costco'

    def on_start(self, md, order, service, account):
        service.add_time_trigger(service.time(11, 0, 0))
        service.add_time_trigger(service.time(13, 0, 0))
        self.bought = 0
        
        
    def on_timer(self, event, md, order, service, account):
        if self.bought == 0:
            self.bought = 1
            order.algo_buy('COST',algorithm='market',intent = 'init',order_quantity = 100)
            order.algo_buy('SPY',algorithm='market',intent='init',order_quantity = 100)
        else:
            if account[self.symbol].position.shares != 0 and self.bought == 1:
                order.algo_sell('COST',algorithm='market',intent='exit')
                order.algo_sell('SPY',algorithm='market',intent='exit')
