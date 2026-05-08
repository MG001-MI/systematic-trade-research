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
