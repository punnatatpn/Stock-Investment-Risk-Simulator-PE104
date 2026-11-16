import random
import math
import statistics


def calculate_volatility(returns):
    if len(returns) < 2:
        raise ValueError("At least two returns are required to calculate volatility.")

    mean_return = sum(returns) / len(returns)

    squared_deviations = []

    for daily_return in returns:
        deviation = daily_return - mean_return
        squared_deviation = deviation ** 2
        squared_deviations.append(squared_deviation)

    variance = sum(squared_deviations) / (len(returns) - 1)

    daily_std_dev = math.sqrt(variance)

    annualized_volatility = daily_std_dev * math.sqrt(252)

    return {
        "mean_daily_return": mean_return,
        "variance": variance,
        "daily_std_dev": daily_std_dev,
        "annualized_volatility": annualized_volatility
    }

def run_monte_carlo(returns, initial_investment, trading_days, simulations, seed=42):
    if not isinstance(returns, list) or len(returns) == 0:
        raise ValueError("Returns must be a non-empty list.")

    if not all(isinstance(r, (int, float)) and not isinstance(r, bool) and math.isfinite(r) and r >= -1 for r in returns):
        raise ValueError("Returns must be finite numbers greater than or equal to -1.")

    if not isinstance(initial_investment, (int, float)) or isinstance(initial_investment, bool) or not math.isfinite(initial_investment) or initial_investment <= 0:
        raise ValueError("Initial investment must be a positive finite number.")

    if not isinstance(trading_days, int) or isinstance(trading_days, bool) or trading_days <= 0:
        raise ValueError("Trading days must be a positive integer.")

    if not isinstance(simulations, int) or isinstance(simulations, bool) or simulations <= 0:
        raise ValueError("Simulations must be a positive integer.")

    rng = random.Random(seed) 

    all_simulations = []

    for simulation in range(simulations):

        portfolio_values = [initial_investment]

        current_value = initial_investment

        for day in range(trading_days):

            daily_return = rng.choice(returns)

            current_value = current_value * (1 + daily_return)

            portfolio_values.append(current_value) 

        all_simulations.append(portfolio_values)

    return all_simulations



