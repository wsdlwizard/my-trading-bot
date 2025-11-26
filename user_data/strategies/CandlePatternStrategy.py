"""
CandlePatternStrategy - A comprehensive Freqtrade strategy using candlestick patterns
and popular technical indicators optimized for crypto markets.

Features:
- 50+ candlestick pattern recognition
- Popular technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Time-of-week analysis for optimal trading periods
- Hyperopt-ready parameters for optimization
"""

import numpy as np
import talib.abstract as ta
from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import pandas_ta as pta


class CandlePatternStrategy(IStrategy):
    """
    A Freqtrade strategy that uses candlestick patterns and technical indicators
    to identify trading opportunities in crypto markets.
    """

    # Strategy interface version
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy
    timeframe = '1h'

    # Can this strategy go on a short position?
    can_short = False

    # Minimal ROI designed for the strategy
    minimal_roi = {
        "0": 0.15,
        "30": 0.10,
        "60": 0.05,
        "120": 0.02,
        "240": 0.01
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Use exit signal
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 200

    # -------------------------------------------------------------------------
    # Hyperopt Parameters for Indicators
    # -------------------------------------------------------------------------

    # RSI parameters
    buy_rsi = IntParameter(20, 40, default=30, space="buy", optimize=True)
    sell_rsi = IntParameter(60, 80, default=70, space="sell", optimize=True)
    rsi_period = IntParameter(7, 21, default=14, space="buy", optimize=True)

    # MACD parameters
    macd_fast = IntParameter(8, 16, default=12, space="buy", optimize=True)
    macd_slow = IntParameter(20, 30, default=26, space="buy", optimize=True)
    macd_signal = IntParameter(7, 12, default=9, space="buy", optimize=True)

    # Bollinger Bands parameters
    bb_period = IntParameter(15, 25, default=20, space="buy", optimize=True)
    bb_std = DecimalParameter(1.5, 3.0, default=2.0, space="buy", optimize=True)

    # EMA parameters
    ema_short = IntParameter(5, 15, default=9, space="buy", optimize=True)
    ema_medium = IntParameter(15, 30, default=21, space="buy", optimize=True)
    ema_long = IntParameter(40, 60, default=50, space="buy", optimize=True)

    # Stochastic parameters
    stoch_k = IntParameter(10, 20, default=14, space="buy", optimize=True)
    stoch_d = IntParameter(2, 5, default=3, space="buy", optimize=True)
    stoch_buy = IntParameter(15, 30, default=20, space="buy", optimize=True)
    stoch_sell = IntParameter(70, 85, default=80, space="sell", optimize=True)

    # ADX parameters
    adx_period = IntParameter(10, 20, default=14, space="buy", optimize=True)
    adx_threshold = IntParameter(20, 35, default=25, space="buy", optimize=True)

    # ATR parameters
    atr_period = IntParameter(10, 20, default=14, space="buy", optimize=True)

    # CCI parameters
    cci_period = IntParameter(15, 25, default=20, space="buy", optimize=True)
    cci_buy = IntParameter(-150, -80, default=-100, space="buy", optimize=True)
    cci_sell = IntParameter(80, 150, default=100, space="sell", optimize=True)

    # Williams %R parameters
    willr_period = IntParameter(10, 20, default=14, space="buy", optimize=True)

    # MFI parameters
    mfi_period = IntParameter(10, 20, default=14, space="buy", optimize=True)
    mfi_buy = IntParameter(15, 30, default=20, space="buy", optimize=True)
    mfi_sell = IntParameter(70, 85, default=80, space="sell", optimize=True)

    # Time of week parameters
    enable_time_filter = CategoricalParameter([True, False], default=True, space="buy", optimize=True)
    best_hour_start = IntParameter(0, 12, default=6, space="buy", optimize=True)
    best_hour_end = IntParameter(12, 23, default=18, space="buy", optimize=True)
    best_day_start = IntParameter(0, 3, default=1, space="buy", optimize=True)  # 0=Monday, 6=Sunday
    best_day_end = IntParameter(3, 6, default=5, space="buy", optimize=True)

    # Candle pattern weights (for hyperopt optimization)
    bullish_pattern_weight = DecimalParameter(0.5, 2.0, default=1.0, space="buy", optimize=True)
    bearish_pattern_weight = DecimalParameter(0.5, 2.0, default=1.0, space="sell", optimize=True)

    # Minimum pattern strength threshold
    min_pattern_strength = IntParameter(1, 5, default=2, space="buy", optimize=True)

    # -------------------------------------------------------------------------
    # Candlestick Pattern Recognition Functions (50+ patterns)
    # -------------------------------------------------------------------------

    def add_candlestick_patterns(self, dataframe: DataFrame) -> DataFrame:
        """
        Add all candlestick pattern indicators to the dataframe.
        Uses TA-Lib for pattern recognition.
        Returns pattern strength as positive (bullish) or negative (bearish).
        """

        # Two Crows - Bearish reversal
        dataframe['CDL_2CROWS'] = ta.CDL2CROWS(dataframe)

        # Three Black Crows - Strong bearish reversal
        dataframe['CDL_3BLACKCROWS'] = ta.CDL3BLACKCROWS(dataframe)

        # Three Inside Up/Down - Reversal patterns
        dataframe['CDL_3INSIDE'] = ta.CDL3INSIDE(dataframe)

        # Three Line Strike - Continuation pattern
        dataframe['CDL_3LINESTRIKE'] = ta.CDL3LINESTRIKE(dataframe)

        # Three Outside Up/Down - Reversal patterns
        dataframe['CDL_3OUTSIDE'] = ta.CDL3OUTSIDE(dataframe)

        # Three Stars in the South - Bullish reversal
        dataframe['CDL_3STARSINSOUTH'] = ta.CDL3STARSINSOUTH(dataframe)

        # Three Advancing White Soldiers - Bullish reversal
        dataframe['CDL_3WHITESOLDIERS'] = ta.CDL3WHITESOLDIERS(dataframe)

        # Abandoned Baby - Strong reversal
        dataframe['CDL_ABANDONEDBABY'] = ta.CDLABANDONEDBABY(dataframe)

        # Advance Block - Bearish reversal
        dataframe['CDL_ADVANCEBLOCK'] = ta.CDLADVANCEBLOCK(dataframe)

        # Belt-hold - Reversal
        dataframe['CDL_BELTHOLD'] = ta.CDLBELTHOLD(dataframe)

        # Breakaway - Reversal
        dataframe['CDL_BREAKAWAY'] = ta.CDLBREAKAWAY(dataframe)

        # Closing Marubozu - Strong momentum
        dataframe['CDL_CLOSINGMARUBOZU'] = ta.CDLCLOSINGMARUBOZU(dataframe)

        # Concealing Baby Swallow - Bullish reversal
        dataframe['CDL_CONCEALBABYSWALL'] = ta.CDLCONCEALBABYSWALL(dataframe)

        # Counterattack - Reversal
        dataframe['CDL_COUNTERATTACK'] = ta.CDLCOUNTERATTACK(dataframe)

        # Dark Cloud Cover - Bearish reversal
        dataframe['CDL_DARKCLOUDCOVER'] = ta.CDLDARKCLOUDCOVER(dataframe)

        # Doji - Indecision
        dataframe['CDL_DOJI'] = ta.CDLDOJI(dataframe)

        # Doji Star - Reversal warning
        dataframe['CDL_DOJISTAR'] = ta.CDLDOJISTAR(dataframe)

        # Dragonfly Doji - Bullish reversal
        dataframe['CDL_DRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)

        # Engulfing Pattern - Strong reversal
        dataframe['CDL_ENGULFING'] = ta.CDLENGULFING(dataframe)

        # Evening Doji Star - Bearish reversal
        dataframe['CDL_EVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)

        # Evening Star - Bearish reversal
        dataframe['CDL_EVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # Gap Side By Side White - Continuation
        dataframe['CDL_GAPSIDESIDEWHITE'] = ta.CDLGAPSIDESIDEWHITE(dataframe)

        # Gravestone Doji - Bearish reversal
        dataframe['CDL_GRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(dataframe)

        # Hammer - Bullish reversal
        dataframe['CDL_HAMMER'] = ta.CDLHAMMER(dataframe)

        # Hanging Man - Bearish reversal
        dataframe['CDL_HANGINGMAN'] = ta.CDLHANGINGMAN(dataframe)

        # Harami Pattern - Reversal
        dataframe['CDL_HARAMI'] = ta.CDLHARAMI(dataframe)

        # Harami Cross - Reversal
        dataframe['CDL_HARAMICROSS'] = ta.CDLHARAMICROSS(dataframe)

        # High Wave Candle - Indecision
        dataframe['CDL_HIGHWAVE'] = ta.CDLHIGHWAVE(dataframe)

        # Hikkake Pattern - Reversal trap
        dataframe['CDL_HIKKAKE'] = ta.CDLHIKKAKE(dataframe)

        # Modified Hikkake - Confirmed reversal trap
        dataframe['CDL_HIKKAKEMOD'] = ta.CDLHIKKAKEMOD(dataframe)

        # Homing Pigeon - Bullish continuation
        dataframe['CDL_HOMINGPIGEON'] = ta.CDLHOMINGPIGEON(dataframe)

        # Identical Three Crows - Bearish reversal
        dataframe['CDL_IDENTICAL3CROWS'] = ta.CDLIDENTICAL3CROWS(dataframe)

        # In-Neck Pattern - Bearish continuation
        dataframe['CDL_INNECK'] = ta.CDLINNECK(dataframe)

        # Inverted Hammer - Bullish reversal
        dataframe['CDL_INVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(dataframe)

        # Kicking - Strong reversal
        dataframe['CDL_KICKING'] = ta.CDLKICKING(dataframe)

        # Kicking by length - Strong reversal
        dataframe['CDL_KICKINGBYLENGTH'] = ta.CDLKICKINGBYLENGTH(dataframe)

        # Ladder Bottom - Bullish reversal
        dataframe['CDL_LADDERBOTTOM'] = ta.CDLLADDERBOTTOM(dataframe)

        # Long Legged Doji - Indecision
        dataframe['CDL_LONGLEGGEDDOJI'] = ta.CDLLONGLEGGEDDOJI(dataframe)

        # Long Line Candle - Strong momentum
        dataframe['CDL_LONGLINE'] = ta.CDLLONGLINE(dataframe)

        # Marubozu - Strong momentum
        dataframe['CDL_MARUBOZU'] = ta.CDLMARUBOZU(dataframe)

        # Matching Low - Bullish reversal
        dataframe['CDL_MATCHINGLOW'] = ta.CDLMATCHINGLOW(dataframe)

        # Mat Hold - Continuation
        dataframe['CDL_MATHOLD'] = ta.CDLMATHOLD(dataframe)

        # Morning Doji Star - Bullish reversal
        dataframe['CDL_MORNINGDOJISTAR'] = ta.CDLMORNINGDOJISTAR(dataframe)

        # Morning Star - Bullish reversal
        dataframe['CDL_MORNINGSTAR'] = ta.CDLMORNINGSTAR(dataframe)

        # On-Neck Pattern - Bearish continuation
        dataframe['CDL_ONNECK'] = ta.CDLONNECK(dataframe)

        # Piercing Line - Bullish reversal
        dataframe['CDL_PIERCING'] = ta.CDLPIERCING(dataframe)

        # Rickshaw Man - Indecision
        dataframe['CDL_RICKSHAWMAN'] = ta.CDLRICKSHAWMAN(dataframe)

        # Rising/Falling Three Methods - Continuation
        dataframe['CDL_RISEFALL3METHODS'] = ta.CDLRISEFALL3METHODS(dataframe)

        # Separating Lines - Continuation
        dataframe['CDL_SEPARATINGLINES'] = ta.CDLSEPARATINGLINES(dataframe)

        # Shooting Star - Bearish reversal
        dataframe['CDL_SHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(dataframe)

        # Short Line Candle - Weak momentum
        dataframe['CDL_SHORTLINE'] = ta.CDLSHORTLINE(dataframe)

        # Spinning Top - Indecision
        dataframe['CDL_SPINNINGTOP'] = ta.CDLSPINNINGTOP(dataframe)

        # Stalled Pattern - Bearish reversal
        dataframe['CDL_STALLEDPATTERN'] = ta.CDLSTALLEDPATTERN(dataframe)

        # Stick Sandwich - Bullish reversal
        dataframe['CDL_STICKSANDWICH'] = ta.CDLSTICKSANDWICH(dataframe)

        # Takuri - Bullish reversal
        dataframe['CDL_TAKURI'] = ta.CDLTAKURI(dataframe)

        # Tasuki Gap - Continuation
        dataframe['CDL_TASUKIGAP'] = ta.CDLTASUKIGAP(dataframe)

        # Thrusting Pattern - Bearish continuation
        dataframe['CDL_THRUSTING'] = ta.CDLTHRUSTING(dataframe)

        # Tristar Pattern - Reversal
        dataframe['CDL_TRISTAR'] = ta.CDLTRISTAR(dataframe)

        # Unique 3 River - Bullish reversal
        dataframe['CDL_UNIQUE3RIVER'] = ta.CDLUNIQUE3RIVER(dataframe)

        # Upside Gap Two Crows - Bearish reversal
        dataframe['CDL_UPSIDEGAP2CROWS'] = ta.CDLUPSIDEGAP2CROWS(dataframe)

        # Upside/Downside Gap Three Methods - Continuation
        dataframe['CDL_XSIDEGAP3METHODS'] = ta.CDLXSIDEGAP3METHODS(dataframe)

        return dataframe

    def calculate_bullish_patterns(self, dataframe: DataFrame) -> DataFrame:
        """
        Calculate aggregate bullish pattern strength.
        Higher values indicate stronger bullish signals.
        """
        bullish_patterns = [
            'CDL_3WHITESOLDIERS', 'CDL_MORNINGSTAR', 'CDL_MORNINGDOJISTAR',
            'CDL_HAMMER', 'CDL_INVERTEDHAMMER', 'CDL_DRAGONFLYDOJI',
            'CDL_PIERCING', 'CDL_HOMINGPIGEON', 'CDL_LADDERBOTTOM',
            'CDL_MATCHINGLOW', 'CDL_STICKSANDWICH', 'CDL_TAKURI',
            'CDL_UNIQUE3RIVER', 'CDL_3STARSINSOUTH', 'CDL_CONCEALBABYSWALL'
        ]

        dataframe['bullish_pattern_sum'] = 0
        for pattern in bullish_patterns:
            if pattern in dataframe.columns:
                # TA-Lib returns positive values for bullish patterns
                dataframe['bullish_pattern_sum'] += (dataframe[pattern] > 0).astype(int)

        # Also count dual patterns that are positive (bullish)
        dual_patterns = [
            'CDL_ENGULFING', 'CDL_HARAMI', 'CDL_HARAMICROSS', 'CDL_BELTHOLD',
            'CDL_BREAKAWAY', 'CDL_COUNTERATTACK', 'CDL_KICKING',
            'CDL_KICKINGBYLENGTH', 'CDL_3INSIDE', 'CDL_3OUTSIDE',
            'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 'CDL_TRISTAR', 'CDL_ABANDONEDBABY'
        ]

        for pattern in dual_patterns:
            if pattern in dataframe.columns:
                dataframe['bullish_pattern_sum'] += (dataframe[pattern] > 0).astype(int)

        return dataframe

    def calculate_bearish_patterns(self, dataframe: DataFrame) -> DataFrame:
        """
        Calculate aggregate bearish pattern strength.
        Higher values indicate stronger bearish signals.
        """
        bearish_patterns = [
            'CDL_3BLACKCROWS', 'CDL_EVENINGSTAR', 'CDL_EVENINGDOJISTAR',
            'CDL_HANGINGMAN', 'CDL_SHOOTINGSTAR', 'CDL_GRAVESTONEDOJI',
            'CDL_DARKCLOUDCOVER', 'CDL_ADVANCEBLOCK', 'CDL_STALLEDPATTERN',
            'CDL_IDENTICAL3CROWS', 'CDL_2CROWS', 'CDL_UPSIDEGAP2CROWS',
            'CDL_INNECK', 'CDL_ONNECK', 'CDL_THRUSTING'
        ]

        dataframe['bearish_pattern_sum'] = 0
        for pattern in bearish_patterns:
            if pattern in dataframe.columns:
                # TA-Lib returns negative values for bearish patterns
                dataframe['bearish_pattern_sum'] += (dataframe[pattern] < 0).astype(int)

        # Also count dual patterns that are negative (bearish)
        dual_patterns = [
            'CDL_ENGULFING', 'CDL_HARAMI', 'CDL_HARAMICROSS', 'CDL_BELTHOLD',
            'CDL_BREAKAWAY', 'CDL_COUNTERATTACK', 'CDL_KICKING',
            'CDL_KICKINGBYLENGTH', 'CDL_3INSIDE', 'CDL_3OUTSIDE',
            'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 'CDL_TRISTAR', 'CDL_ABANDONEDBABY'
        ]

        for pattern in dual_patterns:
            if pattern in dataframe.columns:
                dataframe['bearish_pattern_sum'] += (dataframe[pattern] < 0).astype(int)

        return dataframe

    def add_technical_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        Add popular technical indicators for crypto trading.
        """

        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)

        # MACD - Moving Average Convergence Divergence
        macd = ta.MACD(
            dataframe,
            fastperiod=self.macd_fast.value,
            slowperiod=self.macd_slow.value,
            signalperiod=self.macd_signal.value
        )
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # Bollinger Bands
        bollinger = ta.BBANDS(
            dataframe,
            timeperiod=self.bb_period.value,
            nbdevup=self.bb_std.value,
            nbdevdn=self.bb_std.value
        )
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (
            dataframe['bb_upper'] - dataframe['bb_lower']
        )

        # EMA - Exponential Moving Averages
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=self.ema_short.value)
        dataframe['ema_medium'] = ta.EMA(dataframe, timeperiod=self.ema_medium.value)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=self.ema_long.value)

        # SMA - Simple Moving Averages
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)

        # Stochastic Oscillator
        stoch = ta.STOCH(
            dataframe,
            fastk_period=self.stoch_k.value,
            slowk_period=self.stoch_d.value,
            slowd_period=self.stoch_d.value
        )
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']

        # Stochastic RSI
        stoch_rsi = ta.STOCHRSI(dataframe, timeperiod=14)
        dataframe['stochrsi_k'] = stoch_rsi['fastk']
        dataframe['stochrsi_d'] = stoch_rsi['fastd']

        # ADX - Average Directional Index
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period.value)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe, timeperiod=self.adx_period.value)
        dataframe['minus_di'] = ta.MINUS_DI(dataframe, timeperiod=self.adx_period.value)

        # ATR - Average True Range
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['atr_percent'] = dataframe['atr'] / dataframe['close'] * 100

        # CCI - Commodity Channel Index
        dataframe['cci'] = ta.CCI(dataframe, timeperiod=self.cci_period.value)

        # Williams %R
        dataframe['willr'] = ta.WILLR(dataframe, timeperiod=self.willr_period.value)

        # MFI - Money Flow Index
        dataframe['mfi'] = ta.MFI(dataframe, timeperiod=self.mfi_period.value)

        # OBV - On Balance Volume
        dataframe['obv'] = ta.OBV(dataframe)

        # ROC - Rate of Change
        dataframe['roc'] = ta.ROC(dataframe, timeperiod=10)

        # Momentum
        dataframe['mom'] = ta.MOM(dataframe, timeperiod=10)

        # VWAP - Volume Weighted Average Price (approximate)
        cumulative_volume = dataframe['volume'].cumsum()
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        cumulative_tp_volume = (dataframe['volume'] * typical_price).cumsum()
        # Avoid division by zero when cumulative volume is zero
        dataframe['vwap'] = np.where(
            cumulative_volume > 0,
            cumulative_tp_volume / cumulative_volume,
            typical_price
        )

        # Ichimoku Cloud
        dataframe['ichimoku_conv'] = (
            dataframe['high'].rolling(window=9).max() + 
            dataframe['low'].rolling(window=9).min()
        ) / 2
        dataframe['ichimoku_base'] = (
            dataframe['high'].rolling(window=26).max() + 
            dataframe['low'].rolling(window=26).min()
        ) / 2
        dataframe['ichimoku_span_a'] = (dataframe['ichimoku_conv'] + dataframe['ichimoku_base']) / 2
        dataframe['ichimoku_span_b'] = (
            dataframe['high'].rolling(window=52).max() + 
            dataframe['low'].rolling(window=52).min()
        ) / 2

        # Parabolic SAR
        dataframe['sar'] = ta.SAR(dataframe)

        # SuperTrend (using pandas_ta)
        try:
            supertrend = pta.supertrend(dataframe['high'], dataframe['low'], dataframe['close'], length=10, multiplier=3)
            if supertrend is not None and len(supertrend.columns) > 0:
                dataframe['supertrend'] = supertrend.iloc[:, 0]
                dataframe['supertrend_direction'] = supertrend.iloc[:, 1]
        except Exception:
            dataframe['supertrend'] = dataframe['close']
            dataframe['supertrend_direction'] = 1

        # KAMA - Kaufman Adaptive Moving Average
        dataframe['kama'] = ta.KAMA(dataframe, timeperiod=30)

        # CMF - Chaikin Money Flow (approximate)
        price_range = dataframe['high'] - dataframe['low']
        # Avoid division by zero when high equals low (zero range candles)
        mfv = np.where(
            price_range > 0,
            ((dataframe['close'] - dataframe['low']) - (dataframe['high'] - dataframe['close'])) / price_range * dataframe['volume'],
            0
        )
        rolling_volume = dataframe['volume'].rolling(window=20).sum()
        # Avoid division by zero when rolling volume sum is zero
        dataframe['cmf'] = np.where(
            rolling_volume > 0,
            mfv.rolling(window=20).sum() / rolling_volume,
            0
        )

        # Elder Ray Index
        dataframe['bull_power'] = dataframe['high'] - dataframe['ema_medium']
        dataframe['bear_power'] = dataframe['low'] - dataframe['ema_medium']

        return dataframe

    def add_market_context(self, dataframe: DataFrame) -> DataFrame:
        """
        Add market context indicators for crypto-specific analysis.
        """

        # Trend strength indicator
        dataframe['trend'] = np.where(
            (dataframe['ema_short'] > dataframe['ema_medium']) & 
            (dataframe['ema_medium'] > dataframe['ema_long']),
            1,  # Uptrend
            np.where(
                (dataframe['ema_short'] < dataframe['ema_medium']) & 
                (dataframe['ema_medium'] < dataframe['ema_long']),
                -1,  # Downtrend
                0  # Sideways
            )
        )

        # Volatility regime
        dataframe['volatility_regime'] = np.where(
            dataframe['atr_percent'] > dataframe['atr_percent'].rolling(50).mean() + dataframe['atr_percent'].rolling(50).std(),
            'high',
            np.where(
                dataframe['atr_percent'] < dataframe['atr_percent'].rolling(50).mean() - dataframe['atr_percent'].rolling(50).std(),
                'low',
                'normal'
            )
        )

        # Volume analysis
        dataframe['volume_ma'] = dataframe['volume'].rolling(20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']
        dataframe['high_volume'] = dataframe['volume_ratio'] > 1.5

        # Price momentum
        dataframe['price_change_1h'] = dataframe['close'].pct_change(1) * 100
        dataframe['price_change_4h'] = dataframe['close'].pct_change(4) * 100
        dataframe['price_change_24h'] = dataframe['close'].pct_change(24) * 100

        # Support/Resistance levels (simple pivot points)
        dataframe['pivot'] = (dataframe['high'].shift(1) + dataframe['low'].shift(1) + dataframe['close'].shift(1)) / 3
        dataframe['r1'] = 2 * dataframe['pivot'] - dataframe['low'].shift(1)
        dataframe['s1'] = 2 * dataframe['pivot'] - dataframe['high'].shift(1)
        dataframe['r2'] = dataframe['pivot'] + (dataframe['high'].shift(1) - dataframe['low'].shift(1))
        dataframe['s2'] = dataframe['pivot'] - (dataframe['high'].shift(1) - dataframe['low'].shift(1))

        return dataframe

    def add_time_features(self, dataframe: DataFrame) -> DataFrame:
        """
        Add time-based features for analyzing optimal trading periods.
        """
        dataframe['hour'] = dataframe['date'].dt.hour
        dataframe['day_of_week'] = dataframe['date'].dt.dayofweek
        dataframe['day_of_month'] = dataframe['date'].dt.day
        dataframe['week_of_year'] = dataframe['date'].dt.isocalendar().week
        dataframe['month'] = dataframe['date'].dt.month

        # Weekend indicator
        dataframe['is_weekend'] = dataframe['day_of_week'] >= 5

        # Trading session indicators (in UTC)
        dataframe['is_asian_session'] = (dataframe['hour'] >= 0) & (dataframe['hour'] < 8)
        dataframe['is_european_session'] = (dataframe['hour'] >= 7) & (dataframe['hour'] < 16)
        dataframe['is_us_session'] = (dataframe['hour'] >= 13) & (dataframe['hour'] < 22)

        # Optimal trading window
        dataframe['in_optimal_hours'] = (
            (dataframe['hour'] >= self.best_hour_start.value) & 
            (dataframe['hour'] <= self.best_hour_end.value)
        )
        dataframe['in_optimal_days'] = (
            (dataframe['day_of_week'] >= self.best_day_start.value) & 
            (dataframe['day_of_week'] <= self.best_day_end.value)
        )

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate all indicators used by the strategy.
        """
        # Add candlestick patterns
        dataframe = self.add_candlestick_patterns(dataframe)
        dataframe = self.calculate_bullish_patterns(dataframe)
        dataframe = self.calculate_bearish_patterns(dataframe)

        # Add technical indicators
        dataframe = self.add_technical_indicators(dataframe)

        # Add market context
        dataframe = self.add_market_context(dataframe)

        # Add time features
        dataframe = self.add_time_features(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define conditions for entering a trade.
        """
        conditions = []

        # Condition 1: Bullish candlestick patterns
        conditions.append(
            dataframe['bullish_pattern_sum'] >= self.min_pattern_strength.value
        )

        # Condition 2: RSI oversold
        conditions.append(
            dataframe['rsi'] <= self.buy_rsi.value
        )

        # Condition 3: MACD bullish crossover or positive histogram
        conditions.append(
            (dataframe['macdhist'] > 0) | 
            (dataframe['macd'] > dataframe['macdsignal'])
        )

        # Condition 4: Price at or below lower Bollinger Band
        conditions.append(
            dataframe['close'] <= dataframe['bb_lower'] * 1.01
        )

        # Condition 5: Stochastic oversold
        conditions.append(
            dataframe['stoch_k'] <= self.stoch_buy.value
        )

        # Condition 6: ADX shows trending market
        conditions.append(
            dataframe['adx'] >= self.adx_threshold.value
        )

        # Condition 7: Positive EMA alignment
        conditions.append(
            dataframe['ema_short'] > dataframe['ema_medium']
        )

        # Condition 8: MFI oversold
        conditions.append(
            dataframe['mfi'] <= self.mfi_buy.value
        )

        # Condition 9: CCI oversold
        conditions.append(
            dataframe['cci'] <= self.cci_buy.value
        )

        # Time filter (optional)
        if self.enable_time_filter.value:
            time_condition = (
                dataframe['in_optimal_hours'] & 
                dataframe['in_optimal_days']
            )
        else:
            time_condition = True

        # Volume confirmation
        volume_condition = dataframe['volume'] > 0

        # Entry signal: Need at least 3 conditions to be true + time and volume filters
        # Use len(conditions) to avoid magic number coupling
        condition_sum = sum([c.astype(int) if hasattr(c, 'astype') else int(c) for c in conditions])

        if isinstance(time_condition, bool):
            dataframe.loc[
                (condition_sum >= 3) & 
                volume_condition,
                'enter_long'
            ] = 1
        else:
            dataframe.loc[
                (condition_sum >= 3) & 
                time_condition & 
                volume_condition,
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define conditions for exiting a trade.
        """
        conditions = []

        # Condition 1: Bearish candlestick patterns
        conditions.append(
            dataframe['bearish_pattern_sum'] >= self.min_pattern_strength.value
        )

        # Condition 2: RSI overbought
        conditions.append(
            dataframe['rsi'] >= self.sell_rsi.value
        )

        # Condition 3: MACD bearish crossover
        conditions.append(
            (dataframe['macdhist'] < 0) | 
            (dataframe['macd'] < dataframe['macdsignal'])
        )

        # Condition 4: Price at or above upper Bollinger Band
        conditions.append(
            dataframe['close'] >= dataframe['bb_upper'] * 0.99
        )

        # Condition 5: Stochastic overbought
        conditions.append(
            dataframe['stoch_k'] >= self.stoch_sell.value
        )

        # Condition 6: MFI overbought
        conditions.append(
            dataframe['mfi'] >= self.mfi_sell.value
        )

        # Condition 7: CCI overbought
        conditions.append(
            dataframe['cci'] >= self.cci_sell.value
        )

        # Condition 8: Negative EMA alignment
        conditions.append(
            dataframe['ema_short'] < dataframe['ema_medium']
        )

        # Volume confirmation
        volume_condition = dataframe['volume'] > 0

        # Exit signal: Need at least 2 conditions to be true
        condition_sum = sum([c.astype(int) if hasattr(c, 'astype') else int(c) for c in conditions])

        dataframe.loc[
            (condition_sum >= 2) & 
            volume_condition,
            'exit_long'
        ] = 1

        return dataframe
