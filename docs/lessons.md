# Lessons Learned and Future Improvements

## What the project demonstrates
- A Python program can be divided into modules with clear responsibilities.
- Historical prices must be converted into daily returns before volatility and bootstrap simulation.
- A list of dictionaries is useful for representing dated stock-price records.
- CSV files provide a simple persistent format for historical prices.
- Input validation and exception handling keep terminal programs usable when users make mistakes or files are missing.
- A fixed random seed makes simulation output reproducible.

## Important concepts
- Daily return measures the proportional price change from one observation to the next.
- Volatility measures dispersion of returns; annualization uses the square root of 252 trading days.
- Historical Bootstrap samples observed returns with replacement.
- VaR is a percentile-based loss estimate, not a guaranteed maximum loss.
- Maximum Drawdown measures the largest decline from a running peak.

## Limitations
- Historical returns may not represent future market conditions.
- The current model does not include fees, taxes, slippage, liquidity constraints, or regime changes.
- Yahoo Finance availability and ticker coverage can vary.
- The offline sample is intended for demonstration, not live trading.

## Future improvements
- Add user-selectable confidence levels and random seeds.
- Add a clear data-source timestamp and date range to each report.
- Add tests using Python's `unittest` module.
- Support multiple assets and portfolio weights.
- Compare bootstrap results with a parametric Monte Carlo model.
