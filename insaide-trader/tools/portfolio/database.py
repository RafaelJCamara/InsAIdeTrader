import sqlite3
from datetime import datetime, timezone

DB = "portfolio.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS wallet (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                balance     REAL NOT NULL DEFAULT 0.0
            );

            INSERT OR IGNORE INTO wallet (id, balance) VALUES (1, 0.0);

            CREATE TABLE IF NOT EXISTS holdings (
                symbol      TEXT PRIMARY KEY,
                shares      INTEGER NOT NULL DEFAULT 0,
                avg_cost    REAL NOT NULL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT NOT NULL,
                type        TEXT NOT NULL,  -- 'deposit', 'buy', 'sell'
                symbol      TEXT,
                shares      INTEGER,
                price       REAL,
                total       REAL NOT NULL
            );
        """)


init_db()


# ── Wallet ────────────────────────────────────────────────────────────────

def get_balance() -> float:
    with _get_conn() as conn:
        row = conn.execute("SELECT balance FROM wallet WHERE id = 1").fetchone()
        return row[0] if row else 0.0


def deposit(amount: float) -> float:
    if amount <= 0:
        raise ValueError("Deposit amount must be positive")
    with _get_conn() as conn:
        conn.execute("UPDATE wallet SET balance = balance + ? WHERE id = 1", (amount,))
        return get_balance()


def _debit(amount: float) -> None:
    with _get_conn() as conn:
        conn.execute("UPDATE wallet SET balance = balance - ? WHERE id = 1", (amount,))


def _credit(amount: float) -> None:
    with _get_conn() as conn:
        conn.execute("UPDATE wallet SET balance = balance + ? WHERE id = 1", (amount,))


# ── Holdings ──────────────────────────────────────────────────────────────

def get_all_holdings() -> dict[str, dict]:
    """Return {symbol: {shares, avg_cost}} for positions with shares > 0."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT symbol, shares, avg_cost FROM holdings WHERE shares > 0"
        ).fetchall()
        return {row[0]: {"shares": row[1], "avg_cost": row[2]} for row in rows}


def _upsert_holding(symbol: str, additional_shares: int, price_per_share: float) -> None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT shares, avg_cost FROM holdings WHERE symbol = ?", (symbol,)
        ).fetchone()

        if row:
            old_shares, old_avg = row
            new_shares = old_shares + additional_shares
            if new_shares > 0:
                new_avg = ((old_avg * old_shares) + (price_per_share * additional_shares)) / new_shares
            else:
                new_avg = 0.0
            conn.execute(
                "UPDATE holdings SET shares = ?, avg_cost = ? WHERE symbol = ?",
                (new_shares, new_avg, symbol),
            )
        else:
            conn.execute(
                "INSERT INTO holdings (symbol, shares, avg_cost) VALUES (?, ?, ?)",
                (symbol, additional_shares, price_per_share),
            )


def _reduce_holding(symbol: str, shares_to_sell: int) -> None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT shares FROM holdings WHERE symbol = ?", (symbol,)
        ).fetchone()
        if not row or row[0] < shares_to_sell:
            current = row[0] if row else 0
            raise ValueError(
                f"Not enough shares of {symbol} to sell. "
                f"Current: {current}, requested: {shares_to_sell}"
            )
        new_shares = row[0] - shares_to_sell
        if new_shares == 0:
            conn.execute("DELETE FROM holdings WHERE symbol = ?", (symbol,))
        else:
            conn.execute(
                "UPDATE holdings SET shares = ? WHERE symbol = ?",
                (new_shares, symbol),
            )


def get_holding(symbol: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT shares, avg_cost FROM holdings WHERE symbol = ?", (symbol,)
        ).fetchone()
        if row and row[0] > 0:
            return {"shares": row[0], "avg_cost": row[1]}
        return None


# ── Transactions ──────────────────────────────────────────────────────────

def _record_transaction(tx_type: str, total: float, symbol: str | None = None,
                        shares: int | None = None, price: float | None = None) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO transactions (timestamp, type, symbol, shares, price, total) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), tx_type, symbol, shares, price, total),
        )


def get_transactions(limit: int = 50) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, timestamp, type, symbol, shares, price, total "
            "FROM transactions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {"id": r[0], "timestamp": r[1], "type": r[2], "symbol": r[3],
             "shares": r[4], "price": r[5], "total": r[6]}
            for r in rows
        ]


# ── High-level operations (used by portfolio_management) ─────────────────

def execute_deposit(amount: float) -> float:
    new_balance = deposit(amount)
    _record_transaction("deposit", total=amount)
    return new_balance


def execute_buy(symbol: str, shares: int, price_per_share: float) -> dict:
    total_cost = shares * price_per_share
    balance = get_balance()
    if total_cost > balance:
        raise ValueError(
            f"Insufficient funds. Cost: ${total_cost:.2f}, "
            f"available balance: ${balance:.2f}"
        )
    _debit(total_cost)
    _upsert_holding(symbol, shares, price_per_share)
    _record_transaction("buy", total=total_cost, symbol=symbol, shares=shares, price=price_per_share)
    return {
        "symbol": symbol,
        "shares_bought": shares,
        "price_per_share": price_per_share,
        "total_cost": total_cost,
        "remaining_balance": get_balance(),
    }


def execute_sell(symbol: str, shares: int, price_per_share: float) -> dict:
    _reduce_holding(symbol, shares)
    total_proceeds = shares * price_per_share
    _credit(total_proceeds)
    _record_transaction("sell", total=total_proceeds, symbol=symbol, shares=shares, price=price_per_share)
    return {
        "symbol": symbol,
        "shares_sold": shares,
        "price_per_share": price_per_share,
        "total_proceeds": total_proceeds,
        "remaining_balance": get_balance(),
    }
