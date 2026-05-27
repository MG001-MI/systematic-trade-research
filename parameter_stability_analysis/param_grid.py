#PARAMETER GRID SEARCH

def score_fn(grid_res):

    return (

        grid_res["cagr"] * 0.4 +

        grid_res["sharpe"] * 0.4 +

        grid_res["max_dd"] * 0.2   # already negative → penalizes DD

    )

results = []

for atr_mult in [3.5, 4.0, 4.5, 5.0]:

    for breakout in [15, 18, 20, 22, 25]:

        grid_res = run_backtest(df.copy(), breakout, atr_mult)

        results.append({

            "breakout": breakout,

            "atr": atr_mult,

            "cagr": grid_res["cagr"],

            "sharpe": grid_res["sharpe"],

            "max_dd": grid_res["max_dd"],

            "score": score_fn(grid_res)   # ✅ weighted score

        })

df_results = pd.DataFrame(results)



df_results = df_results.sort_values("score", ascending=False).reset_index(drop=True)

# clean ranking column
df_results.insert(0, "rank", df_results.index + 1)


#df_results.head().style.hide(axis="index")

df_results.head().style.format({

    "atr": "{:.1f}"

}).hide(axis="index")
