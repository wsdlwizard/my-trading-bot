"""Sample trading strategy for Freqtrade."""

from freqtrade.strategy import IStrategy
from pandas import DataFrame


class SampleStrategy(IStrategy):
    """
    Sample strategy demonstrating the basic structure of a Freqtrade strategy.

    This is a simple example strategy that uses RSI and EMA indicators.
    You should customize this strategy for your own trading needs.
    """

    INTERFACE_VERSION = 3

    # Minimal ROI (Return on Investment) table
    minimal_roi = {
        "60": 0.01,  # 1% profit after 60 minutes
        "30": 0.02,  # 2% profit after 30 minutes
        "0": 0.04,  # 4% profit at any time
    }

    # Stoploss
    stoploss = -0.10  # 10% stop loss

    # Trailing stoploss
    trailing_stop = False

    # Timeframe
    timeframe = "5m"

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # These values can be overridden in the config
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add indicators to the dataframe.

        Args:
            dataframe: OHLCV dataframe with columns open, high, low, close, volume
            metadata: Additional information about the pair

        Returns:
            DataFrame with populated indicators
        """
        # RSI
        dataframe["rsi"] = self.rsi(dataframe, 14)

        # EMA - Exponential Moving Average
        dataframe["ema_short"] = self.ema(dataframe, 9)
        dataframe["ema_long"] = self.ema(dataframe, 21)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Determine entry signals.

        Args:
            dataframe: DataFrame with populated indicators
            metadata: Additional information about the pair

        Returns:
            DataFrame with enter_long column populated
        """
        dataframe.loc[
            (
                (dataframe["rsi"] < 30)
                & (dataframe["ema_short"] > dataframe["ema_long"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Determine exit signals.

        Args:
            dataframe: DataFrame with populated indicators
            metadata: Additional information about the pair

        Returns:
            DataFrame with exit_long column populated
        """
        dataframe.loc[
            (
                (dataframe["rsi"] > 70)
                | (dataframe["ema_short"] < dataframe["ema_long"])
            )
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1

        return dataframe

    @staticmethod
    def rsi(dataframe: DataFrame, period: int = 14) -> DataFrame:
        """Calculate RSI indicator."""
        delta = dataframe["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def ema(dataframe: DataFrame, period: int) -> DataFrame:
        """Calculate EMA indicator."""
        return dataframe["close"].ewm(span=period, adjust=False).mean()
