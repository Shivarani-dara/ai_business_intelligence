
import sqlite3
import pandas as pd

DB_PATH = "sales.db"
CSV_PATH = "data/ai_bi_assistant_sales_data - GET.csv"


def create_database():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_transactions (
            transaction_id TEXT PRIMARY KEY,
            order_date TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT NOT NULL,
            sales_channel TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL,
            discount_amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def load_csv():
    create_database()

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower()

    required_columns = [
        "transaction_id",
        "order_date",
        "product",
        "category",
        "region",
        "sales_channel",
        "quantity",
        "unit_price",
        "discount_amount",
        "status"
    ]

    if not all(col in df.columns for col in required_columns):
        raise ValueError("CSV is missing required columns")

    df = df[required_columns]

    for col in ["quantity", "unit_price", "discount_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    conn = sqlite3.connect(DB_PATH)

    try:
        df.to_sql(
            "sales_staging",
            conn,
            if_exists="replace",
            index=False
        )

        conn.execute("""
            INSERT OR REPLACE INTO sales_transactions (
                transaction_id, order_date, product, category,
                region, sales_channel, quantity, unit_price,
                discount_amount, status
            )
            SELECT
                transaction_id, order_date, product, category,
                region, sales_channel, quantity, unit_price,
                discount_amount, status
            FROM sales_staging
            WHERE transaction_id IS NOT NULL
              AND TRIM(transaction_id) != ''
        """)

        conn.execute("DROP TABLE sales_staging")
        conn.commit()

        return {
            "success": True,
            "records_processed": len(df),
            "records_loaded": conn.execute(
                "SELECT COUNT(*) FROM sales_transactions"
            ).fetchone()[0]
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def inspect_database():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sales_transactions
        LIMIT 5
    """)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()


def create_analytics_view():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE VIEW IF NOT EXISTS valid_sales AS
        SELECT
            transaction_id,
            order_date,
            product,
            category,
            region,
            sales_channel,
            quantity,
            unit_price,
            discount_amount,
            (quantity * unit_price - discount_amount) AS revenue
        FROM sales_transactions
        WHERE
            status = 'Completed'
            AND unit_price IS NOT NULL
            AND quantity > 0
            AND unit_price > 0
            AND discount_amount >= 0
            AND discount_amount <= quantity * unit_price
    """)

    conn.commit()
    conn.close()



def inspect_valid_sales():
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), SUM(revenue)
        FROM valid_sales
    """)

    result = cursor.fetchone()

    print("Valid transactions:", result[0])
    print("Total revenue:", result[1])

    conn.close()


def validate_csv():
    df = pd.read_csv(CSV_PATH)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    required_columns = [
        "transaction_id",
        "order_date",
        "product",
        "category",
        "region",
        "sales_channel",
        "quantity",
        "unit_price",
        "discount_amount",
        "status"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        return {
            "valid": False,
            "missing_columns": missing_columns
        }

    # Convert numeric columns safely
    for col in ["quantity", "unit_price", "discount_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Validate dates (CSV format: DD-MM-YYYY)
    dates = pd.to_datetime(
        df["order_date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    # Identify data-quality issues
    missing_values = df[required_columns].isnull().sum().to_dict()

    duplicate_ids = int(
        df["transaction_id"].duplicated().sum()
    )

    invalid_dates = int(dates.isnull().sum())

    invalid_quantities = int(
        (df["quantity"].isnull() | (df["quantity"] <= 0)).sum()
    )

    invalid_prices = int(
        (df["unit_price"].isnull() | (df["unit_price"] <= 0)).sum()
    )

    invalid_discounts = int(
        (
            (df["discount_amount"].isnull())
            | (df["discount_amount"] < 0)
            | (
                df["discount_amount"]
                > df["quantity"] * df["unit_price"]
            )
        ).sum()
    )

    return {
        "schema_valid": True,
        "data_quality_passed": (
            duplicate_ids == 0
            and invalid_dates == 0
            and invalid_quantities == 0
            and invalid_prices == 0
            and invalid_discounts == 0
        ),
        "total_records": len(df),
        "duplicate_transaction_ids": duplicate_ids,
        "invalid_dates": invalid_dates,
        "invalid_quantities": invalid_quantities,
        "invalid_prices": invalid_prices,
        "invalid_discounts": invalid_discounts,
        "missing_values": {
            key: int(value)
            for key, value in missing_values.items()
        }
    }



if __name__ == "__main__":
    create_analytics_view()
    inspect_valid_sales()