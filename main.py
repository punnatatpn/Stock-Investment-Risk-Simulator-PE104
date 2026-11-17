import os

from data_analysis import load_stock_data, calculate_daily_returns
from simulation import calculate_volatility, run_monte_carlo
from risk_report import calculate_risk, generate_report


def get_ticker():
    """Get and validate a stock ticker from the user."""
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
    """Get a positive finite number from the user."""
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
    """Get a positive integer from the user."""
    while True:
        try:
            value = int(input(prompt))

            if value <= 0:
                print("Please enter an integer greater than zero.")
                continue

            return value

        except ValueError:
            print("Please enter a whole number.")


def run_analysis():
    """Run the complete stock risk analysis workflow."""

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
    os.makedirs(reports_dir, exist_ok=True)

    report_path = os.path.join(reports_dir, "risk_report.txt")

    report = generate_report(analysis, report_path)

    print("\n[4/4] Report generated successfully!")
    print("\n", report)
    print("\nSaved to:", report_path)


def view_previous_report():
    """Display the previously generated risk report."""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(
        base_dir,
        "reports",
        "risk_report.txt"
    )

    if not os.path.exists(report_path):
        print("\nNo previous report found.")
        print("Please run Stock Risk Analysis first.")
        return

    try:
        with open(report_path, "r", encoding="utf-8") as file:
            report = file.read()

        if not report.strip():
            print("\nThe previous report is empty.")
            return

        print("\n" + "=" * 60)
        print("PREVIOUS RISK REPORT")
        print("=" * 60)
        print(report)

    except OSError as error:
        print("\nUnable to read the previous report:", error)



def main():
    """Display the main menu and control the application."""

    while True:
        print("\n" + "=" * 50)
        print("       QUANT STOCK RISK SIMULATOR")
        print("=" * 50)

        print("\nMAIN MENU")
        print("[1] Run Stock Risk Analysis")
        print("[2] View Previous Report")
        print("[3] Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            try:
                run_analysis()

            except Exception as error:
                print("\nAn error occurred:", error)
                print("Please check your input or try again.")

            input("\nPress Enter to return to the main menu...")

        elif choice == "2":
            view_previous_report()
            input("\nPress Enter to return to the main menu...")

        elif choice == "3":
            print("\nThank you for using QUANT Stock Risk Simulator.")
            print("Goodbye!")
            break

        else:
            print("\nInvalid option. Please select 1, 2 or 3.")


if __name__ == "__main__":
    main()
