## BACKTESTING

#------IMPORTING LIBRARIES & OHLC DATA------

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download("AMZN", start="2005-01-01", auto_adjust=True)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

breakout = 20
atr_mult = 3.5


#------STRATEGY------

def run_backtest(df, breakout, atr_mult, slip_factor = 1.0):
    df = df.copy()
    
    df['breakout_high'] = df['High'].shift(1).rolling(breakout).max()
    df['breakout_low'] = df['Low'].shift(1).rolling(breakout).min()
    df['sma200'] = df['Close'].rolling(200).mean()
    df['returns_std'] = df['Close'].pct_change(fill_method=None).rolling(breakout).std()
    df['true_range'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['atr'] = df['true_range'].rolling(14).mean()
    df['returns_std_ma'] = df['returns_std'].rolling(100).mean()
    
    capital = 100000
    cash = capital
    cost = 0.001
    position = 0
    entry_price = 0
    highest_price = None

    position_size = 0.7     #(locked after trying multiple values from 0.5-1)
    
    equity = []
    
    trades = []
    
    entry_idx = None
    
    position_history = []
    
    
    for i in range(len(df)):

        close = df['Close'].iloc[i]
        
        if i == len(df) - 1:
            equity.append(cash + position * close)
            position_history.append(1 if position > 0 else 0)
            break
            
        next_open = df['Open'].iloc[i+1]
        
        breakout_high = df['breakout_high'].iloc[i]
        breakout_low  = df['breakout_low'].iloc[i]
        sma = df['sma200'].iloc[i]
        returns_std = df['returns_std'].iloc[i]
        returns_std_ma = df['returns_std_ma'].iloc[i]
        atr = df['atr'].iloc[i]
        slippage = (0.1 * atr / close) * slip_factor #fixed one was 0.0005

        
        #NaN handling 
        if any(pd.isna(x) for x in [breakout_high, breakout_low, sma, returns_std, returns_std_ma, atr]):
            equity.append(cash + position * close)
            position_history.append(1 if position > 0 else 0)
            continue

            
        #  Entry 
        
        if position == 0:
    
            if close > breakout_high:
    
                entry_price = next_open * (1 + cost/2 + slippage)
                shares = (cash * position_size) / entry_price
                
                position = shares
                cash -= shares * entry_price
                
                highest_price = close
                entry_idx = i # Real cash deduction model 
    
        #  Exit
        
        elif position > 0:
            
            
            if highest_price is None:
                highest_price = close
            else:
                highest_price = max(highest_price, close)
            
            atr_stop = highest_price - atr_mult * atr
            donchian_stop = breakout_low
            
            exit_level = max(donchian_stop, atr_stop)
    
            
            #ATR-based Exit (replaced low20 exit)
            
            if close <  exit_level:
                    exit_price = next_open * (1 - cost/2 - slippage)
                   
                    pnl = (exit_price - entry_price) / entry_price
                    duration = i - entry_idx
                    trades.append((pnl, duration)) 
        
                    cash += position * exit_price
                    position = 0
                    entry_price = 0
                    entry_idx = None
                    highest_price = None
    
        #  Equity
        
        equity.append(cash + position * close)
        position_history.append(1 if position > 0 else 0)
    
    
        #  Performance metrics
    
    equity = pd.Series(equity, index=df.index)
    
    # Returns
    
    returns = equity.pct_change()
    
    # CAGR(time-based)
    
    years = (df.index[-1] - df.index[0]).days / 365.25
    
    if years > 0:
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1
    else:
        cagr = np.nan
    
    # Vol / Sharpe
    
    if returns.std() > 0:
        vol_ann = returns.std() * np.sqrt(252)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
    else:
        vol_ann = sharpe = np.nan
        
    # Sortino
    
    downside = returns[returns < 0]
    sortino = (returns.mean() / downside.std()) * np.sqrt(252) if downside.std() > 0 else np.nan

    downside = returns[returns < 0]

    if len(downside) > 0 and downside.std() > 0:
        sortino = (returns.mean() / downside.std()) * np.sqrt(252)
    else:
        sortino = np.nan
        
    # Drawdowns
    
    cum_max = equity.cummax()
    drawdown = equity / cum_max - 1
    
    max_dd = drawdown.min()
    avg_dd = drawdown[drawdown < 0].mean()
    
    # Drawdown Duration
    
    dd_flag = (drawdown < 0).astype(int)
    
    dd_duration = (
        dd_flag.groupby((dd_flag != dd_flag.shift()).cumsum())
        .cumsum()
    )
    
    max_dd_duration = dd_duration.max()
    avg_dd_duration = dd_duration[dd_duration > 0].mean()
    
    
    #  Trade Stats
    
    if len(trades) > 0:
        trade_returns = np.array([t[0] for t in trades])
        trade_durations = np.array([t[1] for t in trades])
    
        win_rate = (trade_returns > 0).mean()
    
        wins = trade_returns[trade_returns > 0]
        losses = trade_returns[trade_returns < 0]
    
        profit_factor = (
            wins.sum() / abs(losses.sum())
            if len(losses) > 0 else np.nan
        )
    
        expectancy = trade_returns.mean()
        best_trade = trade_returns.max()
        worst_trade = trade_returns.min()
    
        max_trade_duration = trade_durations.max()
        avg_trade_duration = trade_durations.mean()
    
        # SQN
        
        if len(trade_returns) > 1 and trade_returns.std() > 0:
            sqn = (trade_returns.mean() / trade_returns.std()) * np.sqrt(len(trade_returns))
        else:
            sqn = np.nan
    
        # Kelly
        if len(wins) > 0 and len(losses) > 0:
            kelly = win_rate - (1 - win_rate) / (wins.mean() / abs(losses.mean()))
        else:
            kelly = np.nan
    
    else:
        win_rate = profit_factor = expectancy = np.nan
        best_trade = worst_trade = np.nan
        max_trade_duration = avg_trade_duration = sqn = kelly = np.nan
    
    # Exposure
    
    exposure = np.mean(position_history)
    
    # Buy & Hold
    
    buy_hold = df['Close'].iloc[-1] / df['Close'].iloc[0] - 1
    
    
    # returning results
    
    return {
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "vol_ann": vol_ann,
        "max_dd": max_dd,
        "avg_dd": avg_dd,

        
        "max_dd_duration": max_dd_duration,
        "avg_dd_duration": avg_dd_duration,
        
        "trades": trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "sqn": sqn,
        "kelly": kelly,
        
        "exposure": exposure,
        "buy_hold": buy_hold,
        "equity": equity
    }
