# Freqtrade Candlestick Pattern Trading Bot

A comprehensive Freqtrade trading strategy that uses candlestick patterns and popular technical indicators to identify trading opportunities in cryptocurrency markets.

## Features

### 🕯️ Candlestick Pattern Recognition (50+ Patterns)

The strategy recognizes over 50 candlestick patterns including:

**Bullish Reversal Patterns:**
- Three White Soldiers
- Morning Star / Morning Doji Star
- Hammer / Inverted Hammer
- Dragonfly Doji
- Piercing Line
- Bullish Engulfing
- Bullish Harami

**Bearish Reversal Patterns:**
- Three Black Crows
- Evening Star / Evening Doji Star
- Hanging Man / Shooting Star
- Gravestone Doji
- Dark Cloud Cover
- Bearish Engulfing
- Bearish Harami

**Continuation Patterns:**
- Rising/Falling Three Methods
- Mat Hold
- Tasuki Gap
- Separating Lines

**Indecision Patterns:**
- Doji variants
- Spinning Top
- High Wave Candle

### 📊 Technical Indicators

**Momentum Indicators:**
- RSI (Relative Strength Index)
- Stochastic Oscillator
- Stochastic RSI
- Williams %R
- CCI (Commodity Channel Index)
- MFI (Money Flow Index)
- ROC (Rate of Change)
- Momentum

**Trend Indicators:**
- MACD (Moving Average Convergence Divergence)
- EMA (Exponential Moving Average) - Short, Medium, Long
- SMA (Simple Moving Average) - 20, 50, 200
- ADX (Average Directional Index)
- Parabolic SAR
- SuperTrend
- KAMA (Kaufman Adaptive Moving Average)
- Ichimoku Cloud

**Volatility Indicators:**
- Bollinger Bands
- ATR (Average True Range)

**Volume Indicators:**
- OBV (On Balance Volume)
- CMF (Chaikin Money Flow)
- Volume Moving Average
- Volume Ratio

**Other:**
- Elder Ray (Bull/Bear Power)
- VWAP (Volume Weighted Average Price)
- Pivot Points (Support/Resistance)

### ⏰ Time-of-Week Analysis

Optimize trading based on:
- Hour of day (configurable optimal trading hours)
- Day of week (configurable optimal trading days)
- Weekend detection
- Trading session awareness (Asian, European, US)

### 🎯 Hyperopt Optimization

Multiple loss functions for strategy optimization:
- **SharpeHyperOptLoss**: Maximize risk-adjusted returns
- **SortinoHyperOptLoss**: Focus on downside risk
- **CalmarHyperOptLoss**: Balance return vs maximum drawdown
- **WinRateProfitFactorLoss**: Optimize win rate and profit quality
- **CryptoOptimizedLoss**: Custom multi-factor optimization for crypto

## Installation

### Prerequisites

- Python 3.8+
- TA-Lib (system library)

### Install TA-Lib (System Library)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**macOS:**
```bash
brew install ta-lib
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Main Config (`config.json`)

The default configuration is set up for:
- Binance exchange (spot trading)
- USDT as stake currency
- Dry run mode enabled
- 5 max open trades
- Top 15 crypto pairs

Edit `config.json` to customize:
- Exchange API keys
- Trading pairs
- Risk parameters
- Telegram notifications
- API server settings

### Hyperopt Config (`config_hyperopt.json`)

Optimized configuration for backtesting and hyperopt with a smaller pair set.

## Usage

### Running the Bot

```bash
# Dry run (paper trading)
freqtrade trade --config config.json --strategy CandlePatternStrategy

# Live trading (update config with API keys first)
freqtrade trade --config config.json --strategy CandlePatternStrategy --dry-run false
```

### Backtesting

```bash
# Download data first
freqtrade download-data --config config.json --days 365 --timeframe 1h

# Run backtest
freqtrade backtesting --config config.json --strategy CandlePatternStrategy --timerange 20230101-20231231
```

### Hyperopt Optimization

```bash
# Download data for hyperopt
freqtrade download-data --config config_hyperopt.json --days 180 --timeframe 1h

# Run hyperopt with Sharpe ratio optimization
freqtrade hyperopt --config config_hyperopt.json --strategy CandlePatternStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --spaces buy sell \
    --epochs 500

# Run hyperopt with crypto-optimized loss
freqtrade hyperopt --config config_hyperopt.json --strategy CandlePatternStrategy \
    --hyperopt-loss CryptoOptimizedLoss \
    --spaces buy sell roi stoploss \
    --epochs 1000
```

### Available Hyperopt Spaces

- `buy`: Optimize entry indicators and thresholds
- `sell`: Optimize exit indicators and thresholds
- `roi`: Optimize return-on-investment table
- `stoploss`: Optimize stop loss value
- `trailing`: Optimize trailing stop parameters

## Strategy Parameters

### Entry Conditions

The strategy enters trades when multiple conditions align:
1. Bullish candlestick patterns detected
2. RSI in oversold territory
3. MACD showing bullish momentum
4. Price near lower Bollinger Band
5. Stochastic oversold
6. ADX showing trending market
7. Positive EMA alignment
8. MFI oversold
9. CCI oversold
10. Within optimal trading hours/days (optional)

### Exit Conditions

The strategy exits trades when:
1. Bearish candlestick patterns detected
2. RSI overbought
3. MACD bearish crossover
4. Price near upper Bollinger Band
5. Stochastic overbought
6. MFI overbought
7. CCI overbought
8. Negative EMA alignment

### Risk Management

Default settings:
- Stop loss: -10%
- Trailing stop: Enabled
- Trailing stop positive: 1%
- Trailing stop offset: 3%
- ROI targets: 15% (immediate) → 1% (240 min)

## Customization

### Adding New Indicators

Edit `user_data/strategies/CandlePatternStrategy.py`:

```python
def add_technical_indicators(self, dataframe: DataFrame) -> DataFrame:
    # Add your custom indicator
    dataframe['my_indicator'] = custom_calculation(dataframe)
    return dataframe
```

### Adding New Hyperopt Parameters

```python
# In CandlePatternStrategy class
my_param = IntParameter(10, 50, default=30, space="buy", optimize=True)

# Use in populate_entry_trend
conditions.append(dataframe['my_indicator'] > self.my_param.value)
```

### Time-Based Filtering

Adjust optimal trading windows:
```python
best_hour_start = IntParameter(0, 12, default=6, space="buy", optimize=True)
best_hour_end = IntParameter(12, 23, default=18, space="buy", optimize=True)
best_day_start = IntParameter(0, 3, default=1, space="buy", optimize=True)
best_day_end = IntParameter(3, 6, default=5, space="buy", optimize=True)
```

## Market Analysis

### Market Context Features

The strategy provides market context analysis:
- **Trend detection**: Uptrend, Downtrend, Sideways
- **Volatility regime**: High, Normal, Low
- **Volume analysis**: Volume ratio and high volume detection
- **Price momentum**: 1h, 4h, 24h price changes

## File Structure

```
my-trading-bot/
├── config.json                           # Main configuration
├── config_hyperopt.json                  # Hyperopt configuration
├── requirements.txt                      # Python dependencies
├── README.md                             # This file
└── user_data/
    ├── strategies/
    │   └── CandlePatternStrategy.py      # Main strategy
    └── hyperopts/
        └── CandlePatternHyperOpt.py      # Custom loss functions
```

## Performance Tips

1. **Start with backtesting**: Always backtest before live trading
2. **Use hyperopt**: Optimize parameters for your specific pairs
3. **Consider timeframes**: Strategy is optimized for 1h, adjust for others
4. **Monitor drawdown**: Keep max_open_trades reasonable
5. **Time filtering**: Enable time filtering to avoid low-volume periods
6. **Pair selection**: Focus on liquid pairs with good volume

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

⚠️ **Trading cryptocurrencies involves significant risk. This bot is for educational purposes only. Always do your own research and never trade with money you cannot afford to lose.**
# my-trading-bot

A trading bot built with [Freqtrade](https://www.freqtrade.io/), an open-source cryptocurrency trading bot.

## Features

- Sample trading strategy with RSI and EMA indicators
- Ready-to-use project structure for Freqtrade
- Configuration templates for easy setup

## Requirements

- Python 3.10 or higher
- Freqtrade 2024.1 or higher

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/wsdlwizard/my-trading-bot.git
   cd my-trading-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. For development, install with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Project Structure

```
my-trading-bot/
├── my_trading_bot/
│   ├── __init__.py
│   └── strategies/
│       ├── __init__.py
│       └── sample_strategy.py
├── user_data/
│   ├── config.json
│   └── strategies/
├── tests/
│   └── test_sample_strategy.py
├── pyproject.toml
└── README.md
```

## Usage

### Running with Freqtrade

1. Configure your exchange API keys in `user_data/config.json`

2. Run in dry-run mode (paper trading):
   ```bash
   freqtrade trade --config user_data/config.json --strategy SampleStrategy --strategy-path my_trading_bot/strategies
   ```

3. Backtest your strategy:
   ```bash
   freqtrade backtesting --config user_data/config.json --strategy SampleStrategy --strategy-path my_trading_bot/strategies
   ```

### Creating Your Own Strategy

1. Copy the sample strategy:
   ```bash
   cp my_trading_bot/strategies/sample_strategy.py my_trading_bot/strategies/my_strategy.py
   ```

2. Modify the strategy class and logic in your new file

3. Update the strategy name in `user_data/config.json`

## Testing

Run tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=my_trading_bot
```

## Linting

Run ruff to lint the code:
```bash
ruff check .
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk. Trading cryptocurrencies involves significant risk of loss. Always do your own research before trading.
