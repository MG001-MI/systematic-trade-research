#------FIXED PARAMS WALKFORWARD TESTING------

def walkforward(df, breakout, atr_mult, train_years=6, test_years=2):

    df = df.copy()
    df['year'] = df.index.year

    years = sorted(df['year'].unique())

    results = []

    start_idx = 0


    while True:
        train_start = years[start_idx]
        train_end   = train_start + train_years - 1
        test_end    = train_end + test_years

        # stop if not enough data
        if test_end > years[-1]:
            break

        # slice
        train_df = df[(df['year'] >= train_start) & (df['year'] <= train_end)].copy()
        test_df  = df[(df['year'] > train_end)  & (df['year'] <= test_end)].copy()

        # run ONLY on test (since params are frozen)

        test_res = run_backtest(test_df, breakout, atr_mult)

        results.append({

            "train_period": f"{train_start}-{train_end}",
            "test_period": f"{train_end+1}-{test_end}",
        
            "cagr": test_res["cagr"],
            "sharpe": test_res["sharpe"],
            "sortino": test_res["sortino"],
            "vol_ann": test_res["vol_ann"],
        
            "max_dd": test_res["max_dd"],
            "avg_dd": test_res["avg_dd"],
            "max_dd_duration": test_res["max_dd_duration"],
            "avg_dd_duration": test_res["avg_dd_duration"],
        
            "trades": test_res["trades"],
            "win_rate": test_res["win_rate"],
            "profit_factor": test_res["profit_factor"],
            "expectancy": test_res["expectancy"],
        
            "best_trade": test_res["best_trade"],
            "worst_trade": test_res["worst_trade"],
            "sqn": test_res["sqn"],
            "kelly": test_res["kelly"],
                    
            "exposure": test_res["exposure"],
            "buy_hold": test_res["buy_hold"]
        })

        start_idx += test_years  # roll forward

    return pd.DataFrame(results)



#------ROLLING WINDOW WALKFORWARD OPTIMIZATION------

def walkforward_optimized(df, params, train_years=6, test_years=2):

    df = df.copy()
    df["year"] = df.index.year
    years = sorted(df["year"].unique())

    results = []
    start_idx = 0

    while True:
        train_start = years[start_idx]
        train_end = train_start + train_years - 1
        test_end = train_end + test_years

        if test_end > years[-1]:
            break

        #  Slice Data 
        train_df = df[(df["year"] >= train_start) & (df["year"] <= train_end)].copy()
        test_df  = df[(df["year"] > train_end) & (df["year"] <= test_end)].copy()

        #  Optimization (Train only)
        best_score = -1e9
        best_params = None
        best_train_res = None

        for breakout, atr in params:
            train_res = run_backtest(train_df.copy(), breakout, atr)

            score = score_fn(train_res)

            if score > best_score:
                best_score = score
                best_params = (breakout, atr)
                best_train_res = train_res

        #  Test (OOS)
        test_res = run_backtest(test_df.copy(), best_params[0], best_params[1])

        results.append({
            "train_period": f"{train_start}-{train_end}",
            "test_period": f"{train_end+1}-{test_end}",

            "breakout": best_params[0],
            "atr": round(best_params[1], 1),

            "train_cagr": best_train_res["cagr"],
            "train_sharpe": best_train_res["sharpe"],
            "train_max_dd": best_train_res["max_dd"],
            "train_win_rate": best_train_res["win_rate"],

            "test_cagr": test_res["cagr"],
            "test_sharpe": test_res["sharpe"],
            "test_max_dd": test_res["max_dd"],

            "test_win_rate": test_res["win_rate"],

            "test_trades": len(test_res["trades"]),
        })

        start_idx += test_years  # roll forward

    return pd.DataFrame(results)
    


#------WALKFORWARD CONSISTENCY CHECK (LOSS CLUSTERING ANALYSIS)------


def consistency_check(series):

    neg = (series < 0).astype(int)

    streaks = neg.groupby((neg != neg.shift()).cumsum()).cumsum()

    return {

        "max_consecutive_losses": int(streaks.max()),

        "worst_3_period_loss_cluster": float(neg.rolling(3).mean().max())

    }
    

rolling_consistency = consistency_check(wf_opt["test_cagr"])

fixed_consistency = consistency_check(wf["cagr"])

consistency_df = pd.DataFrame([
    {
        "walkforward_type": "rolling",
        **rolling_consistency
    },

    {
        "walkforward_type": "fixed",
        **fixed_consistency
    }
])





