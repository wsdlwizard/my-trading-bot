"""Tests for the SampleStrategy."""

import pandas as pd
import pytest

from my_trading_bot.strategies.sample_strategy import SampleStrategy


class TestSampleStrategy:
    """Test cases for SampleStrategy."""

    @pytest.fixture
    def strategy(self):
        """Create a strategy instance for testing."""
        return SampleStrategy({})

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample OHLCV dataframe for testing."""
        data = {
            "open": [100.0, 101.0, 102.0, 103.0, 104.0] * 10,
            "high": [105.0, 106.0, 107.0, 108.0, 109.0] * 10,
            "low": [95.0, 96.0, 97.0, 98.0, 99.0] * 10,
            "close": [102.0, 103.0, 104.0, 105.0, 106.0] * 10,
            "volume": [1000.0, 1100.0, 1200.0, 1300.0, 1400.0] * 10,
        }
        return pd.DataFrame(data)

    def test_strategy_interface_version(self, strategy):
        """Test that strategy has correct interface version."""
        assert strategy.INTERFACE_VERSION == 3

    def test_strategy_timeframe(self, strategy):
        """Test that strategy has a timeframe set."""
        assert strategy.timeframe == "5m"

    def test_strategy_stoploss(self, strategy):
        """Test that strategy has a stoploss set."""
        assert strategy.stoploss == -0.10

    def test_strategy_minimal_roi(self, strategy):
        """Test that strategy has minimal ROI set."""
        assert "0" in strategy.minimal_roi
        assert "30" in strategy.minimal_roi
        assert "60" in strategy.minimal_roi

    def test_rsi_calculation(self, strategy, sample_dataframe):
        """Test RSI calculation."""
        rsi = strategy.rsi(sample_dataframe, 14)
        assert len(rsi) == len(sample_dataframe)
        # RSI should be between 0 and 100 (excluding NaN values)
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()

    def test_ema_calculation(self, strategy, sample_dataframe):
        """Test EMA calculation."""
        ema = strategy.ema(sample_dataframe, 9)
        assert len(ema) == len(sample_dataframe)
        # EMA should be a positive value
        assert (ema > 0).all()

    def test_populate_indicators(self, strategy, sample_dataframe):
        """Test that populate_indicators adds required columns."""
        result = strategy.populate_indicators(sample_dataframe, {"pair": "BTC/USDT"})
        assert "rsi" in result.columns
        assert "ema_short" in result.columns
        assert "ema_long" in result.columns

    def test_populate_entry_trend(self, strategy, sample_dataframe):
        """Test that populate_entry_trend adds enter_long column."""
        df = strategy.populate_indicators(sample_dataframe, {"pair": "BTC/USDT"})
        result = strategy.populate_entry_trend(df, {"pair": "BTC/USDT"})
        assert "enter_long" in result.columns

    def test_populate_exit_trend(self, strategy, sample_dataframe):
        """Test that populate_exit_trend adds exit_long column."""
        df = strategy.populate_indicators(sample_dataframe, {"pair": "BTC/USDT"})
        df = strategy.populate_entry_trend(df, {"pair": "BTC/USDT"})
        result = strategy.populate_exit_trend(df, {"pair": "BTC/USDT"})
        assert "exit_long" in result.columns
