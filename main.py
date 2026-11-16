import os

from data_analysis import load_stock_data, calculate_daily_returns
from simulation import calculate_volatility, run_monte_carlo
from risk_report import calculate_risk, generate_report


def get_ticker():
    while True:
        ticker = input(
            "Enter stock ticker (e.g. AAPL or PTT.BK): "
        ).strip().upper()

        if not ticker:
            print("Ticker cannot be empty.")
            continue

        if not any(char.isalpha() for char in ticker):
            print("Ticker must contain letters.")
            continue

        if not all(char.isalnum() or char == "." for char in ticker):
            print("Only letters, numbers and dots are allowed.")
            continue

        return ticker


def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))

            if not (value > 0 and value < float("inf")):
                print("Please enter a positive finite number.")
                continue

            return value

        except ValueError:
            print("Please enter a valid number.")


def get_positive_integer(prompt):
    while True:
        try:
            value = int(input(prompt))

            if value <= 0:
                print("Please enter an integer greater than zero.")
                continue

            return value

        except ValueError:
            print("Please enter a whole number.")


def main():
    print("=" * 50)
    print("       QUANT STOCK RISK SIMULATOR")
    print("=" * 50)

    ticker = get_ticker()

    initial_investment = get_positive_float(
        "Initial investment: "
    )

    trading_days = get_positive_integer(
        "Trading days: "
    )

    simulations = get_positive_integer(
        "Number of simulations: "
    )

    confidence_level = 0.95

    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base_dir, "sample_data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "stock_prices.csv")

    print("\n[1/4] Loading stock data...")

    try:
        stock_data = load_stock_data(csv_path, ticker)

        if not stock_data:
            print("No stock data available. Please check the ticker.")
            return

        prices = [record["close"] for record in stock_data]

        daily_returns = calculate_daily_returns(prices)

        if len(daily_returns) < 2:
            print("Not enough data to calculate volatility.")
            return

        print("Stock data loaded successfully.")

        print("\n[2/4] Calculating volatility...")

        volatility_results = calculate_volatility(daily_returns)

        print(
            "Annualized Volatility:",
            f"{volatility_results['annualized_volatility']:.2%}"
        )

        print("\n[3/4] Running Monte Carlo simulation...")

        simulation_paths = run_monte_carlo(
            daily_returns,
            initial_investment,
            trading_days,
            simulations
        )

        print(
            "Simulation completed:",
            len(simulation_paths),
            "paths"
        )

        risk_results = calculate_risk(
            simulation_paths,
            initial_investment,
            confidence_level
        )

        analysis = {
            "ticker": stock_data[0]["ticker"],
            "initial_investment": initial_investment,
            "trading_days": trading_days,
            "simulations": simulations,
            "confidence_level": confidence_level,
            **volatility_results,
            **risk_results
        }

        reports_dir = os.path.join(base_dir, "reports")
        report_path = os.path.join(reports_dir, "risk_report.txt")

        report = generate_report(analysis, report_path)

        print("\n[4/4] Report generated successfully!")
        print("\n", report)
        print("\nSaved to:", report_path)

    except Exception as error:
        print("\nAn error occurred:", error)
        print("Please check your input or try again later.")


if __name__ == "__main__":
    main()
