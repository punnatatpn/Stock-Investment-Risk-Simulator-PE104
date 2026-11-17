# PE104 Project Requirements

## Purpose
Build a terminal-only Python application that analyzes historical stock prices, simulates hypothetical investment outcomes, evaluates risk, and saves a readable report.

## User and platform requirements
- Run from the project root with `python main.py` (or `python3 main.py` where required).
- Use a repeating terminal menu until option `0` is selected.
- No graphical user interface or web application.
- Validate user inputs and ask again when invalid.
- Provide a local sample-data demonstration that does not require internet access.

## Programming requirements
- Use functions with docstrings and return values.
- Use lists and dictionaries, including a nested structure such as a list of dictionaries.
- Read and write CSV/text files.
- Include exception handling for invalid input, missing files, and file/data errors.
- Use at least six functions across the project.
- External packages must be documented and justified.

## Functional requirements
1. Retrieve or load historical daily closing prices.
2. Calculate daily returns.
3. Calculate daily and annualized volatility.
4. Run Historical Bootstrap Monte Carlo simulations.
5. Calculate probability of loss, Value at Risk (VaR), and Maximum Drawdown (MDD).
6. Display and save a formatted report.
7. Allow users to view the previous report.

## Data and dependencies
- Bundled examples live in `sample_data/stock_prices.csv`.
- Live Yahoo Finance downloads are cached separately under `data/cache/`.
- Python standard library handles CSV, math, random simulation, and file operations.
- `yfinance` is the only direct third-party dependency.

## Evidence required before submission
- Execute and record at least five test cases, including invalid inputs and missing/corrupt data.
- Save a genuine terminal transcript in `demo_output.txt`.
- Keep an honest AI log with actual results and corrections.
- Maintain six distinguishable source versions as features are developed. Do not invent historical versions after the fact.
