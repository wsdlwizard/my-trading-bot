"""
Custom hyperopt loss functions for CandlePatternStrategy optimization.
Provides multiple loss functions optimized for crypto trading:
- Sharpe Ratio based loss
- Sortino Ratio based loss
- Calmar Ratio based loss
- Win Rate + Profit Factor combined loss
"""

from datetime import datetime
from typing import Any, Dict
from pandas import DataFrame
import numpy as np

from freqtrade.optimize.hyperopt import IHyperOptLoss
from freqtrade.data.metrics import calculate_sharpe, calculate_sortino, calculate_calmar

# Constants
MIN_AVG_LOSS_FALLBACK = 0.0001  # Fallback value when no losing trades exist
MIN_TRADES_REQUIRED = 20  # Minimum number of trades for valid optimization
MAX_LOSS_PENALTY = 100.0  # Penalty returned when constraints are not met


class SharpeHyperOptLoss(IHyperOptLoss):
    """
    Optimize for maximum Sharpe ratio.
    Sharpe ratio measures risk-adjusted returns.
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Dict,
        processed: Dict[str, DataFrame],
        backtest_stats: Dict[str, Any],
        *args,
        **kwargs
    ) -> float:
        """
        Calculate loss based on Sharpe ratio.
        Lower values are better for hyperopt.
        """
        # Minimum trades filter
        if trade_count < MIN_TRADES_REQUIRED:
            return MAX_LOSS_PENALTY

        sharpe = calculate_sharpe(results, min_date, max_date)

        # Return negative sharpe (we want to maximize sharpe, but hyperopt minimizes)
        if sharpe is None or np.isnan(sharpe):
            return MAX_LOSS_PENALTY

        return -sharpe


class SortinoHyperOptLoss(IHyperOptLoss):
    """
    Optimize for maximum Sortino ratio.
    Sortino ratio only penalizes downside volatility.
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Dict,
        processed: Dict[str, DataFrame],
        backtest_stats: Dict[str, Any],
        *args,
        **kwargs
    ) -> float:
        """
        Calculate loss based on Sortino ratio.
        """
        if trade_count < MIN_TRADES_REQUIRED:
            return MAX_LOSS_PENALTY

        sortino = calculate_sortino(results, min_date, max_date)

        if sortino is None or np.isnan(sortino):
            return MAX_LOSS_PENALTY

        return -sortino


class CalmarHyperOptLoss(IHyperOptLoss):
    """
    Optimize for maximum Calmar ratio.
    Calmar ratio measures return relative to maximum drawdown.
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Dict,
        processed: Dict[str, DataFrame],
        backtest_stats: Dict[str, Any],
        *args,
        **kwargs
    ) -> float:
        """
        Calculate loss based on Calmar ratio.
        """
        if trade_count < MIN_TRADES_REQUIRED:
            return MAX_LOSS_PENALTY

        calmar = calculate_calmar(results, min_date, max_date)

        if calmar is None or np.isnan(calmar):
            return MAX_LOSS_PENALTY

        return -calmar


class WinRateProfitFactorLoss(IHyperOptLoss):
    """
    Combined loss function optimizing for win rate and profit factor.
    Balanced approach for crypto trading.
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Dict,
        processed: Dict[str, DataFrame],
        backtest_stats: Dict[str, Any],
        *args,
        **kwargs
    ) -> float:
        """
        Calculate combined loss from win rate and profit factor.
        """
        if trade_count < MIN_TRADES_REQUIRED:
            return MAX_LOSS_PENALTY

        # Calculate win rate
        winning_trades = len(results[results['profit_ratio'] > 0])
        win_rate = winning_trades / trade_count if trade_count > 0 else 0

        # Calculate profit factor
        gross_profit = results[results['profit_ratio'] > 0]['profit_ratio'].sum()
        gross_loss = abs(results[results['profit_ratio'] < 0]['profit_ratio'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Calculate total profit
        total_profit = results['profit_ratio'].sum()

        # Combined score (weighted)
        # Win rate: 30%, Profit factor: 40%, Total profit: 30%
        score = (win_rate * 0.3) + (min(profit_factor, 5) / 5 * 0.4) + (min(max(total_profit, 0), 1) * 0.3)

        return -score


class CryptoOptimizedLoss(IHyperOptLoss):
    """
    Custom loss function optimized specifically for crypto markets.
    Takes into account:
    - Sharpe ratio
    - Maximum drawdown
    - Win rate
    - Average profit per trade
    - Expectancy
    """

    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Dict,
        processed: Dict[str, DataFrame],
        backtest_stats: Dict[str, Any],
        *args,
        **kwargs
    ) -> float:
        """
        Calculate crypto-optimized loss function.
        """
        # Minimum trades requirement
        if trade_count < MIN_TRADES_REQUIRED:
            return MAX_LOSS_PENALTY

        # Get stats
        total_profit = results['profit_ratio'].sum()
        winning_trades = len(results[results['profit_ratio'] > 0])
        losing_trades = len(results[results['profit_ratio'] <= 0])
        win_rate = winning_trades / trade_count

        # Average win/loss
        avg_win = results[results['profit_ratio'] > 0]['profit_ratio'].mean() if winning_trades > 0 else 0
        avg_loss = abs(results[results['profit_ratio'] <= 0]['profit_ratio'].mean()) if losing_trades > 0 else MIN_AVG_LOSS_FALLBACK

        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

        # Sharpe ratio
        sharpe = calculate_sharpe(results, min_date, max_date)
        if sharpe is None or np.isnan(sharpe):
            sharpe = 0

        # Maximum drawdown (from backtest stats)
        max_drawdown = backtest_stats.get('max_drawdown', 0.5)

        # Profit factor
        gross_profit = results[results['profit_ratio'] > 0]['profit_ratio'].sum()
        gross_loss = abs(results[results['profit_ratio'] < 0]['profit_ratio'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit

        # Composite score calculation
        # Higher is better, we negate for hyperopt minimization

        # Sharpe component (normalized to 0-1, max 3)
        sharpe_score = min(max(sharpe, 0), 3) / 3

        # Drawdown component (lower is better, invert)
        drawdown_score = max(1 - abs(max_drawdown), 0)

        # Win rate component
        win_rate_score = win_rate

        # Profit factor component (normalized, max 3)
        pf_score = min(profit_factor, 3) / 3

        # Expectancy component (normalized)
        exp_score = min(max(expectancy + 0.1, 0), 0.2) / 0.2

        # Total profit component (normalized)
        profit_score = min(max(total_profit, 0), 1)

        # Weighted combination
        composite_score = (
            sharpe_score * 0.20 +      # Risk-adjusted returns
            drawdown_score * 0.20 +     # Capital preservation
            win_rate_score * 0.15 +     # Consistency
            pf_score * 0.20 +           # Profit quality
            exp_score * 0.15 +          # Statistical edge
            profit_score * 0.10         # Raw returns
        )

        return -composite_score
