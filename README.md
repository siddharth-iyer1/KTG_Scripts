# KTG_Scripts
### Collection of algorithmic trading and related projects from KTG Summer '22

#### Descriptions of Directories and Programs:

##### Alert Scripts: Contains both active and old alert scripts.
  
  ###### Active Scripts Include:
    Siddharth's Big Alert Script - Class that consolidates most of my alerts, sent out to traders at the 
    office. Some alerts aren't able to run within this class, so they are stand alone.
      Within Big Alert Script:
        New 12 Month Highs - Run during trading hours, notifies for new highs, approaching new highs
        New 12 Month Lows - Run during trading hours, notifies for new lows, approaching new lows
        High Volume - Run during trading hours, notifies when a stock trades close to opening volume
        Earnings Gaps - Run during trading hours, periodically updates on earnings trades that have gapped
        up/down significantly, used to watch behavior in comparison to other earnings day examples
      
    Inside Day Alerts - Run at the start of trading hours, returns alerts for all stocks who saw an inside
    day the previous day
      
    NYSE High Notional Imbalances - Run as closing imbalance approaches, returns alerts for all stocks with
    imbalances of +- 100,000,000 shares

  ##### 12 Month HL Trading Scripts:
    Contains 12 Month Highs and 12 Month Lows scripts used exclusively for forward testing without alerts.
    
  ##### Backtest Programs:
    This contains any trading scripts used for optimizing strategies. These will often have multiple
    versions of the same script with small strategy modifications.
    The optimized versions of these will be put into their respective "Trading Scripts" folders.
  
  ##### Other Projects:
    Random other stuff I work on. Research/Data Analysis for traders at the office
    
  ##### Trailing Long Stop:
    Single stock trading script used for creating a trailing stop. Stop price is determined by target
    and initial risk (determined by initial stock price).
      Looking to fix this for long-term use and create a script that works for short positions as well!
