from cloudquant.interfaces import Strategy, Event
import ktgfunc

# Pulls data for Index VWAP signals

class Gr8Script9dbee58bc1e7497693c14827ecb57474(Strategy):
    __script_name__ = 'Cavan Project'

    @classmethod
    def is_symbol_qualified(cls, symbol, md, service, account):
        
        #return md.stat.prev_close >= 20 and md.stat.avol >= 1000000
        
        return True

    def on_start(self, md, order, service, account):
        service.add_time_trigger(service.time(10, 50))
        self.entry_data = {}
        self.timeok = 0

    def on_timer(self, event, md, order, service, account):
    
        self.timeok = 1
    
    def on_minute_bar(self, event, md, order, service, account, bar):
    
        if self.timeok == 1:
            # Volume Stats
        
            self.entry_data['Total Volume'] = md.L1.minute_volume
            self.entry_data['Ask Volume'] = md.L1.minute_askvol
            self.entry_data['Bid Volume'] = md.L1.minute_bidvol
            self.entry_data['Accumulated Volume'] = md.L1.acc_volume
            self.entry_data['Percent Accumulated Volume'] = str(100*(md.L1.acc_volume/md.stat.avol)) + '%'
        
            # Percent ATR
            
            self.entry_data['Percent ATR'] = str(100*(md.L1.daily_high - md.L1.daily_low)/md.stat.atr) + '%'
        
            # Prints
            
            self.entry_data['Ask Price'] = md.L1.ask
            self.entry_data['Bid Price'] = md.L1.bid
            self.entry_data['Spread'] = abs(md.L1.ask - md.L1.bid)
            
            self.entry_data['Avg Ask Size'] = md.L1.agr_ask_size
            self.entry_data['Avg Bid Size'] = md.L1.agr_bid_size
               
            order.algo_buy(self.symbol,algorithm='market',intent = 'init',order_quantity = 100, collect=self.entry_data)
            

    def on_fill(self, event, md, order, service, account):
        order.algo_sell(self.symbol,algorithm='market',intent = 'exit')
