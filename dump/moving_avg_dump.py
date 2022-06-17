from cloudquant.interfaces import Strategy, Event
import ktgfunc
import talib

class Gr8Script96cff36e80a74607a7bf36a295008af8(Strategy):
    __script_name__ = 'moving_avg_scalp'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
        # Identify stocks with high volatility, price and volume
        
        return ( (md.stat.prev_close >= 50) and 
                 (md.stat.avol >= 1000000) and
                 (md.stat.atr >= 10) )

    def on_start(self, md, order, service, account):
        
        print(md.symbol)
        
        self.bar_data           = []            
        self.moving_avg         = []            # List of moving averages
        self.buySignal          = 0             # Buy Signal
        self.check_flag         = 0             # After 20 minutes, raise
        self.index              = 0             # Index for moving average list. Checks crossover
        self.sellSignal         = 0             # Sell signal
        self.latest_buy         = 0             # Buy price
        
        pass
    
    def on_minute_bar(self, event, md, order, service, account, bar): 
        # Calculate moving average for last 20 min
        if(len(md.bar.minute(start = -5).close) >= 5):
            moving_avg = sum(md.bar.minute(start=-5).close)/5
            if((md.L1.last <= (moving_avg - 2)) and account[self.symbol].position.shares == 0):        # Local min
                order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=100)
        else:
            pass
        
    def on_trade(self, event, md, order, service, account):
        if(account[self.symbol].position.shares != 0):
            short_price = (account[self.symbol].position.capital_short/account[self.symbol].position.shares)
            if(md.L1.last < (short_price - 2)):
                order.algo_buy(self.symbol, algorithm='market', intent='exit')
                print("Covered short position")
            elif ((md.L1.last > (short_price + 4))):
                order.algo_buy(self.symbol, algorithm='market', intent='exit')
                print("Stopped out")

                
                
                
                