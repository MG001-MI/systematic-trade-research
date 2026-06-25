#------PARAMETER GRID STABILITY------

#  PARAM STABILITY TEST FOR BACKTEST


# IMPORTING LIBRARIES & OHLC DATA

import pandas as pd

import numpy as np

import matplotlib.pyplot as plt

from backtesting import run_backtest


# Param stability function

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

#clean ranking column

df_results.insert(0, "rank", df_results.index + 1)

return df_results

---------------------------------------------------------------------
#  PARAM STABILITY TEST FOR ROLLING WINDOW WALKFORWARD


stability = (

    wf_opt[['breakout','atr']]

    .value_counts()

    .reset_index(name='count')

)

stability['pct_windows'] = (

    stability['count']

    / stability['count'].sum()

)

stability.to_csv(

    "results/walkforwards/rolling_window_walkforward_test/rolling_wf_param_stability/parameter_stability.csv",

    index=False

)

return stability



























