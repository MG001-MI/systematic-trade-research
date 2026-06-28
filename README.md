# systematic-trade-research

End-to-end systematic breakout trend-following research pipeline featuring backtesting, parameter robustness analysis, walk-forward optimization, integrated transaction cost modelling and execution engine simulation.

Core features:

Donchian breakout trend-following system with SMA200 trend filter and ATR-based trailing risk management.

Backtest over 20+ years of historical stock data (liquid stocks). This research notebook uses AMZ (Amazon) OHLC data for demonstration.

Parameter stability analysis over multiple regimes.

Slippage stress testing over multiple regimes.

Integrated real-world transaction costs like commissions and slippage.

Fixed-parameter walk-forward validation.

Rolling window walk-forward validation.

Walk-forward consistency analysis (loss clustering).

Live execution engine simulation.

Backtest vs execution engine validation.





## Strategy

**Universe**
- Daily OHLC data for liquid stocks. This pipeline uses AMZ (Amazon) data.

**Entry Logic**
- Long entry on Donchian breakout above the previous N-day high.
- Trades only when price is above the 200-day SMA.
- Orders executed at the next bar's open.

**Exit Logic**
- Exit using the higher of:
  - ATR-based trailing stop, or
  - Donchian lower breakout level.
- Exit orders executed at the next bar's open.

**Position Sizing**
- Configurable fixed-fraction position sizing (Used 70% allocation per trade in this experiment)
  
**Transaction Cost & Slippage Model**
- Commission applied on both entry and exit.
- ATR-based dynamic slippage model scaled by a configurable slippage factor.

  
  


## Research Pipeline

Backtest

→ Parameter Stability

→ Slippage Stress Test

→ Fixed Walk-Forward Validation

→ Rolling Walk-Forward Optimization

→ Walk-Forward Consistency Analysis

→ Live Execution Engine Simulation

→ Backtest vs Execution Engine Validation






## Folder Structure

notebooks/

src/

results/

|
|̵notbooks/
         |̵equity





## Key Findings

- Stable parameter region (breakout,atr = 20,3.5) identified using robustness analysis

- Strategy validated using both fixed and rolling walk-forward testing.

- Transaction cost sensitivity evaluated through slippage stress testing.

- Live execution engine exactly matches backtest results.
  

  


## How to Run

1. Install dependencies from requirements.txt.

2. Run the notebooks in the notebooks/ folder.

3. Exported outputs are saved under results/.
