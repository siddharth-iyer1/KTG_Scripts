from cloudquant.interfaces import Strategy

class CQ59124a45993f4afa8b45f9f5ff5d97f3(Strategy):
    __script_name__ = '6_month_lows'
    
    @classmethod 
    def is_symbol_qualified(cls, symbol, md, service, account):
        return ((md.stat.prev_close >= 20) and
               (md.stat.avol >= 1000000))
            
    def on_start(self, md, order, service, account):
        print(md.symbol)
        
        bars = md.bar.daily(start = -132, end = -1)
        bars_low = bars.low
        low = min(bars.low)
        print('The 6-month low is ' + str(low))
        print('---------------------------------')
        
        self.qualified = ((md.stat.prev_close - low)/low)
        self.low = low
    
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares == 0 and self.qualified >= 0.04):                       # Must be new position and trading 4% above low
            if(md.L1.last >= 1.02*self.low):                                                            # Stock has broken low barrier
                order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=100)     # Short
                print('Opened position on ' + str(md.symbol) + ' at ' + str(account[self.symbol].position.entry_price))
                
        # Scalp after 3% profit or stop out after 3% loss
        if(account[self.symbol].position.shares != 0):
            if(md.L1.last > 1.03*(account[self.symbol].position.entry_price) or
              md.L1.last < 0.97*(account[self.symbol].position.entry_price)):
                order.algo_buy(self.symbol, algorithm='market', intent='exit')
