from agents import function_tool
from tools.market.market import get_share_price
from tools.portfolio.database import (
    execute_buy,
    execute_sell,
    execute_deposit,
    get_all_holdings,
    get_balance,
)


@function_tool
def get_wallet_balance() -> str:
    """Gets the current cash balance available in the wallet.

    Returns:
        str: A message with the current wallet balance.
    """
    balance = get_balance()
    return f"Current wallet balance: ${balance:.2f}"


@function_tool
def deposit_money(amount: float) -> str:
    """Deposits money into the wallet so it can be used to buy stocks.

    Args:
        amount: The dollar amount to deposit. Must be positive.

    Returns:
        str: Confirmation with the new wallet balance.
    """
    try:
        new_balance = execute_deposit(amount)
        return f"Deposited ${amount:.2f}. New wallet balance: ${new_balance:.2f}"
    except ValueError as e:
        return f"Deposit failed: {e}"


@function_tool
def get_current_portfolio_holdings() -> str:
    """Gets the current portfolio holdings for the user.

    Returns:
        str: A summary of current holdings including shares, average cost,
             and current market value per position, plus the wallet balance.
    """
    holdings = get_all_holdings()
    balance = get_balance()

    if not holdings:
        return f"Portfolio is empty. Wallet balance: ${balance:.2f}"

    lines = []
    total_market_value = 0.0
    total_cost_basis = 0.0

    for symbol, info in holdings.items():
        shares = info["shares"]
        avg_cost = info["avg_cost"]
        current_price = get_share_price(symbol)
        market_value = shares * current_price
        cost_basis = shares * avg_cost
        total_market_value += market_value
        total_cost_basis += cost_basis
        pnl = market_value - cost_basis
        lines.append(
            f"{symbol}: {shares} shares | avg cost ${avg_cost:.2f} | "
            f"current ${current_price:.2f} | value ${market_value:.2f} | P&L ${pnl:+.2f}"
        )

    overall_pnl = total_market_value - total_cost_basis
    lines.append(f"\nTotal market value: ${total_market_value:.2f}")
    lines.append(f"Total cost basis: ${total_cost_basis:.2f}")
    lines.append(f"Overall P&L: ${overall_pnl:+.2f}")
    lines.append(f"Wallet balance (cash): ${balance:.2f}")

    return "\n".join(lines)


@function_tool
def buy_stock(symbol: str, shares: int) -> str:
    """Buys a specified number of shares of a stock at the current market price.
    The total cost is deducted from the wallet balance.

    Args:
        symbol: The stock ticker symbol to buy (e.g. AAPL).
        shares: The number of shares to buy. Must be positive.

    Returns:
        str: Confirmation with trade details, or an error if funds are insufficient.
    """
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price <= 0:
        return f"Could not get a valid price for {symbol}. Trade cancelled."

    try:
        result = execute_buy(symbol, shares, price)
        return (
            f"Bought {result['shares_bought']} shares of {symbol} "
            f"at ${result['price_per_share']:.2f}/share. "
            f"Total cost: ${result['total_cost']:.2f}. "
            f"Remaining balance: ${result['remaining_balance']:.2f}"
        )
    except ValueError as e:
        return f"Buy failed: {e}"


@function_tool
def sell_stock(symbol: str, shares: int) -> str:
    """Sells a specified number of shares of a stock at the current market price.
    The proceeds are credited back to the wallet balance.

    Args:
        symbol: The stock ticker symbol to sell (e.g. AAPL).
        shares: The number of shares to sell. Must be positive.

    Returns:
        str: Confirmation with trade details, or an error if not enough shares are held.
    """
    symbol = symbol.upper()
    price = get_share_price(symbol)
    if price <= 0:
        return f"Could not get a valid price for {symbol}. Trade cancelled."

    try:
        result = execute_sell(symbol, shares, price)
        return (
            f"Sold {result['shares_sold']} shares of {symbol} "
            f"at ${result['price_per_share']:.2f}/share. "
            f"Total proceeds: ${result['total_proceeds']:.2f}. "
            f"Remaining balance: ${result['remaining_balance']:.2f}"
        )
    except ValueError as e:
        return f"Sell failed: {e}"
