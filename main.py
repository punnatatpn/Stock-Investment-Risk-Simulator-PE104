"""Main menu and workflow for QUANT Stock Investment Risk Simulator."""

import csv
import math
import os

from data_analysis import load_stock_data, calculate_daily_returns
from simulation import calculate_volatility, run_monte_carlo
from risk_report import calculate_risk, generate_report


def get_ticker():
    """Ask for a ticker and return it after basic validation."""
    while True:
        ticker = input("Enter stock ticker (e.g. AAPL or PTT.BK): ").strip().upper()
        if not ticker:
            print("Ticker cannot be empty.")
        elif not any(char.isalpha() for char in ticker):
            print("Ticker must contain letters.")
        elif not all(char.isalnum() or char == "." for char in ticker):
            print("Only letters, numbers and dots are allowed.")
        else:
            return ticker


def get_positive_float(prompt):
    """Return a positive finite float entered by the user."""
    while True:
        try:
            value = float(input(prompt).strip())
            if math.isfinite(value) and value > 0:
                return value
            print("Please enter a positive finite number.")
        except ValueError:
            print("Please enter a valid number.")


def get_positive_integer(prompt):
    """Return a positive integer entered by the user."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            print("Please enter an integer greater than zero.")
        except ValueError:
            print("Please enter a whole number.")


def load_sample_data(sample_path, ticker="AAPL"):
    """Read and validate a ticker's historical prices from sample CSV data."""
    records = []
    seen_dates = set()
    try:
        with open(sample_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required = {"date", "ticker", "close"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("Sample CSV must contain date, ticker, close columns.")

            for row_number, row in enumerate(reader, start=2):
                if (row.get("ticker") or "").strip().upper() != ticker.upper():
                    continue
                try:
                    date = row["date"].strip()
                    close = float(row["close"])
                    if not math.isfinite(close) or close <= 0:
                        raise ValueError
                except (ValueError, TypeError, AttributeError):
                    print(f"Skipping invalid sample CSV row {row_number}.")
                    continue
                if date in seen_dates:
                    continue
                seen_dates.add(date)
                records.append({"date": date, "ticker": ticker.upper(), "close": close})
    except FileNotFoundError:
        print("Sample data file was not found:", sample_path)
        return []
    except (OSError, csv.Error, ValueError) as error:
        print("Could not read sample data:", error)
        return []

    records.sort(key=lambda item: item["date"])
    return records


def run_analysis(ticker_override=None, use_sample=False):
    """Run data loading, return analysis, simulation, risk assessment and report."""
    ticker = ticker_override or get_ticker()
    initial_investment = get_positive_float("Initial investment: ")
    trading_days = get_positive_integer("Trading days: ")
    simulations = get_positive_integer("Number of simulations: ")
    confidence_level = 0.95

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if use_sample:
        csv_path = os.path.join(base_dir, "sample_data", "stock_prices.csv")
        print("\nDEMO MODE: using the bundled sample CSV; no internet is required.")
        stock_data = load_sample_data(csv_path, ticker)
    else:
        cache_dir = os.path.join(base_dir, "data", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        csv_path = os.path.join(cache_dir, "stock_prices.csv")
        print("\n[1/4] Loading stock data from Yahoo Finance...")
        stock_data = load_stock_data(csv_path, ticker)

    if not stock_data:
        print("No stock data available. Check the ticker or sample dataset.")
        return None

    prices = [record["close"] for record in stock_data]
    daily_returns = calculate_daily_returns(prices)
    if len(daily_returns) < 2:
        print("At least three valid price records are required.")
        return None

    print("Stock data loaded:", len(stock_data), "price records.")
    print("\n[2/4] Calculating volatility...")
    volatility_results = calculate_volatility(daily_returns)
    print("Annualized Volatility:", f"{volatility_results['annualized_volatility']:.2%}")

    print("\n[3/4] Running Historical Bootstrap Monte Carlo...")
    simulation_paths = run_monte_carlo(
        daily_returns, initial_investment, trading_days, simulations
    )
    print("Simulation completed:", len(simulation_paths), "paths")

    risk_results = calculate_risk(
        simulation_paths, initial_investment, confidence_level
    )
    analysis = {
        "ticker": ticker,
        "initial_investment": initial_investment,
        "trading_days": trading_days,
        "simulations": simulations,
        "confidence_level": confidence_level,
        **volatility_results,
        **risk_results,
    }

    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "risk_report.txt")
    report = generate_report(analysis, report_path)

    print("\n[4/4] Report generated successfully!")
    print("\n" + report)
    print("\nSaved to:", report_path)
    return analysis


def view_previous_report():
    """Read, display and return the previously saved report, if available."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(base_dir, "reports", "risk_report.txt")
    if not os.path.exists(report_path):
        print("\nNo previous report found. Run an analysis first.")
        return None
    try:
        with open(report_path, "r", encoding="utf-8") as file:
            report = file.read()
        if not report.strip():
            print("\nThe previous report is empty.")
            return None
        print("\n" + "=" * 60)
        print("PREVIOUS RISK REPORT")
        print("=" * 60)
        print(report)
        return report
    except OSError as error:
        print("\nUnable to read the previous report:", error)
        return None


def main():
    """Display the repeating terminal menu until the user selects 0."""
    while True:
        print("\n" + "=" * 50)
        print("       QUANT STOCK RISK SIMULATOR")
        print("=" * 50)
        print("\nMAIN MENU")
        print("[1] Run Stock Risk Analysis (Yahoo Finance)")
        print("[2] View Previous Report")
        print("[3] Run Demo Using Sample Data (offline)")
        print("[0] Exit")

        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            try:
                run_analysis()
            except (ValueError, TypeError, OSError, KeyError) as error:
                print("\nAnalysis could not be completed:", error)
            except Exception as error:
                print("\nUnexpected error:", error)
            input("\nPress Enter to return to the main menu...")
        elif choice == "2":
            view_previous_report()
            input("\nPress Enter to return to the main menu...")
        elif choice == "3":
            try:
                run_analysis("AAPL", use_sample=True)
            except (ValueError, TypeError, OSError, KeyError) as error:
                print("\nDemo could not be completed:", error)
            except Exception as error:
                print("\nUnexpected error:", error)
            input("\nPress Enter to return to the main menu...")
        elif choice == "0":
            print("\nThank you for using QUANT Stock Risk Simulator.")
            print("Goodbye!")
            return 0
        else:
            print("\nInvalid option. Please select 0, 1, 2 or 3.")


if __name__ == "__main__":
    main()
