# SLIPPAGE STRESS TESTS GRID ANALYSIS

params = [
    (18, 3.5), (20, 3.5), (22, 3.5), (25, 3.5),

    (18, 4.0), (20, 4.0), (22, 4.0), (25, 4.0),

    (18, 4.5), (20, 4.5), (22, 4.5), (25, 4.5),

    (18, 5.0), (20, 5.0), (22, 5.0), (25, 5.0)
]

def slippage_test_grid(df, params, factors=[0.5, 1.0, 2.0]):

    rows = []

    for breakout, atr in params:

        for factor in factors:

            slip_res = run_backtest(df.copy(), breakout, atr, slip_factor=factor)

            rows.append({

                "breakout": breakout,

                "atr": atr,

                "slip": factor,

                "cagr": slip_res["cagr"],

                "sharpe": slip_res["sharpe"],

                "max_dd": slip_res["max_dd"],

                "score": score_fn(slip_res)

            })
    
    # Was return pd.DataFrame(rows) earlier, did the below to prevent the index starting from 1
    
    df_out = pd.DataFrame(rows)
    # sort → higher score = better

    df_out = df_out.sort_values("score", ascending=False).reset_index(drop=True)

    # rank column

    df_out.insert(0, "rank", df_out.index + 1)

    return df_out

slippage_test_grid(df, params).head().style.format({
    "atr": "{:.1f}",
    "slip": "{:.1f}"
}).hide(axis="index")
