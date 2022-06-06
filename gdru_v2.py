from cloudquant.interfaces import Strategy, Event
import ktgfunc
import sys


class gapdown_ripup(Strategy):
    #__script_name__ = 'gapdown_ripup'

    def is_symbol_qualified(cls, symbol, md, service, account):
        
        # Determines if gap down is significant, runs through all symbols in CQ universe
            
            if((md.L1.gap/md.stat.prev_close) <= -0.15):
                # if(shortfloat >= 18%):        Don't think there's a way for me to pull short interest through CQ? placeholder for now
                return True
            else:
                return False

    def on_start(self, md, order, service, account):
        
        # Create timer triggers for the inital buy period (first 30 minutes), Sell period, and market close
        
        service.add_time_trigger(md.market_open_time + service.time_interval(0, 0, 0, 0), repeat_interval=0, timer_id="market_open")
        service.add_time_trigger(md.market_open_time + service.time_interval(0, 0, 0, 0), repeat_interval=0, timer_id="initial_30_min")
        service.add_time_trigger(md.market_open_time + service.time_interval(0, 30, 2, 0), repeat_interval=0, timer_id="sell_period_begin")
        service.add_time_trigger(md.market_close_time + service.time_interval(0, 0, 0, 0), repeat_interval=0, timer_id="market_close")
                
        # Instantiate attributes
        
        self.newHigh = 0                            # New High Value as stock rises
        self.newLow = md.stat.prev_close            # New Low Value to determine where to buy
        self.stopDifference = (md.stat.atr)*0.4     # Arbitrary value gained from ATR, gives me margin for stop
        self.stopValue = 0                          # High Value minus Difference
        self.buy1 = 0                               # First half buy price
        self.buy2 = 0                               # Second half buy price
        self.lowestBuy = 0
        self.bought = 0                             # Flag raised when position is bought
        self.currentATR = 0                         # Percentage of avg 1 day ATR stock has achieved that day        
        pass
    
    def on_timer(self, event, md, order, service, account):
    
         '''
            Each time stock price decreases, set this as new low for the day
            Once stock rises __% above newest low, place buy of x shares, Percent/x placeholders used as 5 and 100, respectively
                Note: We could do the number of shares based on capital. Say we have 100k and want to invest 50k in this stock
                Then we'd divide 25k by the newLow, as this is the latest price, and execute the buy for our first position
                For now, the placeholder remains
            If rise doesn't happen in this time frame, quit
            If rise does happen, use stop difference attribute to determine safety net = buy price minus stop difference*0.5
            stop difference is equal to 1 day ATR - This will be done in the next method
         '''
            
        if(event.timer_id == 'market_open'):            # During initial 30 min
            
            initial_time_flag = 0
            
            while(initial_time_flag == 0):
                if(md.L1.last < self.newLow):           # Update newLow
                    self.newLow = md.L1.last
                    
                if(md.L1.last > self.newLow):           # When rise happens
                    while(md.L1.last > self.newLow):
                        dif = ((md.L1.last - self.newLow)/self.newLow)*100      # Check rise percentage
                        if dif >= 5:                    # Entirely abitrary value, if stock rises 5% above lowest
                            # Buy first position
                            order.algo_buy(self.symbol, algorithm='market', intent='init', order_quantity=100)
                            buy_second_flag = True      # Flag raised to okay the second purchase. If not set,
                                                        # means this loop was never taken, and we never met first buy criteria
                            break
                        else:
                            break
                    if((event.timer_id == 'initial_30_min'):
                        initial_time_flag = 1           # Break out of loop
            
        if(event.timer_id == 'initial_30min' and buy_second_flag == True):
            self.buy1 = account[self.symbol].position.captital_long/account[self.symbol].position.shares    # First buy price/share
            order.algo_buy(self.symbol, algorithm='market', intent='init', order_quantity=100)              # Buy the rest of the position
            self.buy2 = account[self.symbol].position.captital_long/account[self.symbol].position.shares    # Second buy price/share
            
        if(event.timer_id == 'sell_period_begin' and account[self.symbol].position.captital_long == 0):
          sys.exit()                                    # idk how necessary this is. Don't want my script 
                                                        # to short things into infinity if nothing is bought tho
        
        '''
            After every sale, update new high and trailing stop
            If price increases, update new high and stop value to new high minus stop difference
            If/when stop value is equal to 80% of buy price, adjust stop difference to stop difference*0.3
        '''
    
        if(event.timer_id == 'sell_period_begin' and account[self.symbol].position.captital_long != 0):
            # Set our newHigh equal to our average buy price, stop value = buy price minus stop difference
            avg_buy_price = account[self.symbol].position.captital_long/account[self.symbol].position.shares
            self.newHigh = avg_buy_price
            self.stopValue = avg_buy_price - stopDifference
            
            is_market_open = 0
            
            while(is_market_open == 0):  #event.timer_id != 'market_close':                             # Loops continually until market close
                if(md.L1.last > self.newHigh):                                  # Update new high
                    self.newHigh = md.L1.last
                    self.stopValue = self.newHigh - self.stopDifference         # Update stop value
                    if(self.stopValue >= (self.buy1)*0.80):                     # If stop value is equal to 80% of first buy price
                        self.stopDifference *= 0.30                             # Shrink stop value and update
                    self.stopValue = self.newHigh - self.stopDifference
                    
                    
                # Here, we determine where we want to sell. I am deriving this from a stock assumed volatility gained from its ATR
                # We determine whether to wait for higher gains if the potential for profit is 20% ATR greater than our avg buy price
                # If not at certain points in the day, sell off.
                    
                range_movement_neg = -1*(md.L1.daily_low - md.L1.open)                          # Open price to daily low
                range_movement_pos = md.L1.daily_high - md.L1.open                              # Open price to daily high            
                room_for_movement = md.stat.atr - (range_movement_neg + range_movement_pos)     # How much movement we can expect
                achieved_atr = ((range_movement_neg + range_movement_pos)/md.stat.atr)*100      # How much movement has happened (percent)
                
                if(achieved_atr >= 50):     # If > 50%
                    if(md.L1.last + room_for_movement <= ((md.stat.atr)*0.20) + avg_buy_price):
                        order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=200)     # No potential for profit, exit 
                    elif(md.L1.last + room_for_movement >= ((md.stat.atr)*0.20) + avg_buy_price):               # Potential, wait till 75%
                        while(achieved_atr >= 50):
                            if(achieved_atr >= 75):
                                order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=200) # Sell regardless
                                break
                
                if(md.L1.last <= self.stopValue):       # Sell all if stopped out
                    order.algo_sell(self.symbol, algorithm='market', intent='init', order_quantity=200)
                
                if(account[self.symbol].position.captital_long == 0):   # Exit loop when done
                    break
                    
                if(event.timer_id == 'market_close'):
                    is_market_open = 1
        
