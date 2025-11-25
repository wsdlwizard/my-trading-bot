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