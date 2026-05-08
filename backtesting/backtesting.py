#Backtest

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

        
        #NaN handling correction final
        if any(pd.isna(x) for x in [breakout_high, breakout_low, sma, returns_std, returns_std_ma, atr]):
            equity.append(cash + position * close)
            position_history.append(1 if position > 0 else 0)
            continue

            
        # ---------------- ENTRY ----------------
        if position == 0:
    
            if close > breakout_high:
    
                entry_price = next_open * (1 + cost/2 + slippage)
                shares = (cash * position_size) / entry_price
                
                position = shares
                cash -= shares * entry_price
                
                highest_price = close
                entry_idx = i # Real cash deduction model 
    
        # ---------------- EXIT ----------------
        elif position > 0:
            
            
            if highest_price is None:
                highest_price = close
            else:
                highest_price = max(highest_price, close)
            
            atr_stop = highest_price - atr_mult * atr
            donchian_stop = breakout_low
            
            exit_level = max(donchian_stop, atr_stop)
    
            
            # ATR-based exit (replace low20 exit)
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
    
        # ---------------- EQUITY ----------------
        equity.append(cash + position * close)
        position_history.append(1 if position > 0 else 0
