##------LIVE SIMULATION EXECUTION ENGINE------

#------IMPORTING LIBRARIES & OHLC DATA------

import pandas as pd
import numpy as np

#------EXECUTION ENGINE------

class LiveEngine:

    def __init__(self, breakout, atr_mult, initial_capital=100000, slip_factor=1.0, cost=0.001, position_size=0.7):

        self.breakout = breakout
        self.atr_mult = atr_mult

        self.df = pd.DataFrame()

        self.cash = initial_capital
        self.position = 0          # number of shares
        self.entry_price = None
        self.entry_idx = None
        self.highest_price = None

        self.slip_factor = slip_factor
        self.cost = cost
        self.position_size = position_size

        self.pending_order = None  # <-- key: delay execution to next bar

        self.trades = []
        self.equity_curve = []
        
    #  Bar Processing
    
    def on_bar(self, new_row):

        # appended new data
        
        self.df = pd.concat([self.df, new_row.to_frame().T])

        df = self.df.copy()

        # need enough data
        if len(df) < 200:
            return None

        #  Indicators (same as backtest)
        
        df['breakout_high'] = df['High'].shift(1).rolling(self.breakout).max()
        df['breakout_low'] = df['Low'].shift(1).rolling(self.breakout).min()

        df['true_range'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        df['atr'] = df['true_range'].rolling(14).mean()

        i = len(df) - 1

        close = df['Close'].iloc[i]
        signal_close = df['Close'].iloc[i-1]

        
        breakout_high = df['breakout_high'].iloc[i]
        breakout_low = df['breakout_low'].iloc[i]
        
        atr = df['atr'].iloc[i]
        signal_atr   = df['atr'].iloc[i-1]
        

        # Executing Pending Order (at this bar open)
        
        if self.pending_order is not None:

            open_price = df['Open'].iloc[i]
            
            slippage = (0.1 * signal_atr / signal_close) * self.slip_factor
            

            if self.pending_order == "buy":
                entry_price = open_price * (1 + self.cost/2 + slippage)

                shares = (self.cash * self.position_size) / entry_price
                self.position = shares
                self.cash -= shares * entry_price

                self.entry_price = entry_price
                self.entry_idx = i
                self.highest_price = close

            elif self.pending_order == "sell":
                exit_price = open_price * (1 - self.cost/2 - slippage)

                pnl = (exit_price - self.entry_price) / self.entry_price
                duration = i - self.entry_idx

                self.trades.append((pnl, duration))

                self.cash += self.position * exit_price
                self.position = 0
                self.entry_price = None
                self.entry_idx = None
                self.highest_price = None

            self.pending_order = None
            

        #  Exit
        
        #  Updating Trailing Logic
        
        if self.position > 0:
            self.highest_price = max(self.highest_price, close)

            atr_stop = self.highest_price - self.atr_mult * atr
            exit_level = max(breakout_low, atr_stop)

            if close < exit_level:
                self.pending_order = "sell"

        #  Entry
        
        if self.position == 0:
            if close > breakout_high:
                self.pending_order = "buy"

        # Equity Tracking
        
        equity = self.cash + self.position * close
        self.equity_curve.append(equity)

        return {
            "time": df.index[-1],
            "price": close,
            "position": self.position,
            "cash": self.cash,
            "equity": equity
        }
