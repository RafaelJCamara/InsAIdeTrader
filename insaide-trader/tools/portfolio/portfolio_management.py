from agents import function_tool

portfolio = {
    "AAPL": 10,
    "GOOG": 5,
    "TSLA": 2
}

performance = {
    "total_value": 50000.01,
    "percentage_change": 4.17
}

@function_tool
def get_current_portfolio_holdings():
    """Gets the current portfolio holdings for the user.

    Returns:
        dict[str, int]: A dictionary mapping stock symbols to the number of shares held.
    """
    # Placeholder implementation - replace with actual portfolio retrieval logic
    print("Retrieving current portfolio holdings...")
    print(f"Current portfolio: {portfolio}")
    return portfolio

@function_tool
def get_portfolio_performance():
    """Gets the current performance of the user's portfolio.

    Returns:
        dict: A dictionary containing performance metrics such as total value and percentage change.
            - total_value (float): The total current value of the portfolio.
            - percentage_change (float): The percentage change in the portfolio value compared to the previous day. Could be positive or negative.
    """
    print("Calculating portfolio performance...")
    print(f"Portfolio performance: {performance}")
    return performance

@function_tool
def buy_stock(symbol: str, shares: int):
    """Buys a specified number of shares of a stock.

    Args:
        symbol (str): The stock symbol to buy.
        shares (int): The number of shares to buy.
    """
    print(f"Buying {shares} shares of {symbol}...")
    # Placeholder implementation - replace with actual buying logic
    portfolio[symbol] = portfolio.get(symbol, 0) + shares
    print(f"Updated portfolio after buying: {portfolio}")
    performance["total_value"] += shares * 100  # Placeholder for stock price
    performance["percentage_change"] += 0.5  # Placeholder for performance change
    print(f"Updated performance after buying: {performance}")
    
@function_tool
def sell_stock(symbol: str, shares: int):
    """Sells a specified number of shares of a stock.

    Args:
        symbol (str): The stock symbol to sell.
        shares (int): The number of shares to sell.
    """
    print(f"Selling {shares} shares of {symbol}...")
    # Placeholder implementation - replace with actual selling logic
    if symbol in portfolio and portfolio[symbol] >= shares:
        portfolio[symbol] -= shares
        print(f"Updated portfolio after selling: {portfolio}")
        performance["total_value"] -= shares * 100  # Placeholder for stock price
        performance["percentage_change"] -= 0.5  # Placeholder for performance change
        print(f"Updated performance after selling: {performance}")
        if portfolio[symbol] == 0:
            portfolio.pop(symbol)
    else:
        print(f"Not enough shares of {symbol} to sell. Current holdings: {portfolio.get(symbol, 0)}")