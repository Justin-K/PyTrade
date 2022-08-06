# PyTrade TODO List

### TODO
- [ ] Finish SimpleSpotStrategy
  - [ ] Complete the onTradeStart() method
  - [ ] Complete the onTradeComplete() method
  - [ ] Test the restart() method
  - [ ] Test the update() method
  - [ ] Test the tick() method
  - [ ] Make sure that the code in SimpleSpotStrategy.validate() shouldn't be in the validate() method of BaseStrategy
- [ ] Integrate MongoDB into the project
  - [ ] Write a MongoDB wrapper
- [ ] Test the calculatePrice() function.
- [ ] Make some sort of report system to store and present performance statistics to the user.
  - [ ] Make an HTML (report) template
- [ ] Complete the SmartTrade class
  - [ ] Test the SmartTrade class
- [ ] Organize the project into different folders
- [ ] Make/complete a TradingBot class (handler class) to run and manage multiple strategies
- [ ] Review additions to trade.Trade and ensure proper refactor
- [ ] Remove the client attribute of BaseStrategy (bad things happen when multiple strategies use multiple instances of ccxt.Exchange using a single API key)
- [ ] Adapt the trade.Trade class to handle more than 2 orders and successfully calculate the resulting profit
- [ ] Use bid/ask price instead of last?
- [ ] Migrate every class that isn't mean't to be subclassed from base.py to another file
- [ ] Complete the Chart class
- [ ] Add an indicators.py file for technical indicators
### Test
- [ ] Test the Chart class
### Completed
- [x] Complete the updateConfig() method of SimpleSpotStrategy.
- [x] Complete the validate() method
- [x] Test the validate() method
- [x] Complete the tick() method
- [x] Make a config object for the SmartTrade class
