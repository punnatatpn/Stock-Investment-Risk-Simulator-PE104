# QUANT – Stock Investment Risk Simulator

PE104 terminal-based Python project for studying historical stock returns, volatility, Monte Carlo outcomes, and portfolio risk.

## Problem and objective

Stock prices fluctuate over time. This program uses historical closing prices to calculate daily returns and estimate how a hypothetical investment could behave under repeated resampling of historical returns. It is an educational simulator, not an investment recommendation.

## Features

1. Accepts a stock ticker and validates user input.
2. Retrieves historical prices through Yahoo Finance using `yfinance`.
3. Stores downloaded data in `data/cache/stock_prices.csv`; the bundled sample file is kept separate.
4. Calculates daily returns and sample-standard-deviation volatility, annualized using 252 trading days.
5. Runs Historical Bootstrap Monte Carlo simulations using a reproducible random seed.
6. Calculates average, best and worst final portfolio value, probability of loss, percentile loss (VaR), and maximum drawdown.
7. Displays a formatted risk report and saves it to `reports/risk_report.txt`.
8. Offers an offline demo using the bundled AAPL sample data.

## Project structure

```text
Stock-Investment-Risk-Simulator-PE104/
├── main.py
├── data_analysis.py
├── simulation.py
├── risk_report.py
├── README.md
├── requirements.txt
├── .gitignore
├── demo_output.txt
├── sample_data/
│   └── stock_prices.csv
├── data/
│   └── cache/                 # created when live data is downloaded
├── reports/
│   └── risk_report.txt        # created after an analysis
└── docs/
    ├── requirements.md
    ├── test_plan.md
    ├── ai_log.md
    └── lessons.md
```

## Requirements

- Python 3.9 or newer (the project uses `str.removesuffix`).
- Internet connection for live Yahoo Finance data.
- The `yfinance` package for live data retrieval.
- Standard-library modules are used for CSV, validation, calculations, file operations, statistics, and simulation.

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Run

From the project root:

```bash
python3 main.py
```

On systems where `python` points to Python 3, `python main.py` also works.

### Main menu

- `1` – Run live stock risk analysis (internet required).
- `2` – View the previous saved report.
- `3` – Run the offline AAPL sample-data demonstration.
- `0` – Exit.

For the offline demo, choose option 3, then enter values when prompted. It uses `sample_data/stock_prices.csv` and does not download or overwrite that file.

## Methods and assumptions

### Daily return

`daily return = (current close / previous close) - 1`

### Volatility

The program calculates sample variance and sample standard deviation from daily returns. Annualized volatility is daily standard deviation multiplied by the square root of 252.

### Historical Bootstrap Monte Carlo

Each simulated day samples one observed historical daily return with replacement. The sampled return is applied to the current simulated portfolio value. The random seed is fixed at 42 by default to make runs reproducible.

### Risk measures

- Probability of loss: proportion of simulations whose final value is below the initial investment.
- VaR: the selected percentile of simulated monetary losses at the configured confidence level (95% in the main workflow).
- Maximum drawdown: largest percentage decline from a previous running portfolio peak.

## Data and limitations

- Yahoo Finance data availability, ticker formats, network access, and service behavior are outside this project's control.
- Live data is cached in `data/cache/stock_prices.csv`; bundled example data remains in `sample_data/stock_prices.csv`.
- Sample data is historical demonstration data, not a promise of live or current market prices.
- Bootstrap simulation assumes historical daily returns are representative of possible future daily returns. It does not model all market regimes, transaction costs, taxes, liquidity, or changing volatility.
- VaR is a percentile estimate, not the maximum possible loss.
- The output is for coursework and education only. It is not financial advice.

## Team modules

- Member A – `data_analysis.py`: stock data management and daily return calculation.
- Member B – `simulation.py`: volatility analysis and Historical Bootstrap Monte Carlo.
- Member C – `risk_report.py`: risk assessment and investment report.
- `main.py` coordinates the modules and handles the terminal interface.

## Testing and evidence

See `docs/test_plan.md` for test cases and actual execution status. Update the status and evidence only after running each case on the target computer. `demo_output.txt` is a sample transcript; replace or confirm it against a fresh local run before submission.
