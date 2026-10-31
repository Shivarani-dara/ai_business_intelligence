
import sqlite3

DB_PATH = "sales.db"


def get_total_revenue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(revenue)
        FROM valid_sales
    """)

    result = cursor.fetchone()[0]

    conn.close()

    return result



def get_top_product():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT product, SUM(revenue) AS total_revenue
        FROM valid_sales
        GROUP BY product
        ORDER BY total_revenue DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    return result


def get_monthly_revenue():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUBSTR(order_date, 4, 2) AS month,
            SUM(revenue) AS total_revenue
        FROM valid_sales
        GROUP BY month
        ORDER BY CAST(month AS INTEGER)
    """)

    result = cursor.fetchall()
    conn.close()

    return result


def get_top_region():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT region, SUM(revenue) AS total_revenue
        FROM valid_sales
        GROUP BY region
        ORDER BY total_revenue DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    return result




def compare_months(month1, month2):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUBSTR(order_date, 4, 2) AS month,
            SUM(revenue) AS total_revenue
        FROM valid_sales
        WHERE month IN (?, ?)
        GROUP BY month
    """, (month1, month2))

    results = dict(cursor.fetchall())
    conn.close()

    revenue1 = results.get(month1, 0)
    revenue2 = results.get(month2, 0)

    difference = revenue2 - revenue1

    return {
        "month1_revenue": revenue1,
        "month2_revenue": revenue2,
        "difference": difference,
        "percentage_change": (
            (difference / revenue1) * 100
            if revenue1 != 0 else None
        )
    }

def get_dashboard_data(region=None, product=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Build safe, parameterized filters
        conditions = []
        params = []

        if region:
            conditions.append("region = ?")
            params.append(region)

        if product:
            conditions.append("product = ?")
            params.append(product)

        where_clause = (
            "WHERE " + " AND ".join(conditions)
            if conditions else ""
        )

        # 1. Overall business metrics
        cursor.execute(f"""
            SELECT
                COUNT(*),
                COALESCE(SUM(revenue), 0),
                COALESCE(AVG(revenue), 0)
            FROM valid_sales
            {where_clause}
        """, params)

        total_transactions, total_revenue, avg_order_value = cursor.fetchone()

        # 2. Top product
        cursor.execute(f"""
            SELECT product, SUM(revenue)
            FROM valid_sales
            {where_clause}
            GROUP BY product
            ORDER BY SUM(revenue) DESC
            LIMIT 1
        """, params)

        top_product = cursor.fetchone()

        # 3. Top region
        cursor.execute(f"""
            SELECT region, SUM(revenue)
            FROM valid_sales
            {where_clause}
            GROUP BY region
            ORDER BY SUM(revenue) DESC
            LIMIT 1
        """, params)

        top_region = cursor.fetchone()

        # 4. Monthly revenue
        cursor.execute(f"""
            SELECT
                SUBSTR(order_date, 4, 2),
                SUM(revenue)
            FROM valid_sales
            {where_clause}
            GROUP BY SUBSTR(order_date, 4, 2)
            ORDER BY CAST(SUBSTR(order_date, 4, 2) AS INTEGER)
        """, params)

        monthly_revenue = [
            {"month": month, "revenue": revenue}
            for month, revenue in cursor.fetchall()
        ]

        # 5. Revenue by region
        cursor.execute(f"""
            SELECT region, SUM(revenue)
            FROM valid_sales
            {where_clause}
            GROUP BY region
            ORDER BY SUM(revenue) DESC
        """, params)

        region_revenue = [
            {"region": region, "revenue": revenue}
            for region, revenue in cursor.fetchall()
        ]

        # 6. Revenue by product
        cursor.execute(f"""
            SELECT product, SUM(revenue)
            FROM valid_sales
            {where_clause}
            GROUP BY product
            ORDER BY SUM(revenue) DESC
        """, params)

        product_revenue = [
            {"product": product, "revenue": revenue}
            for product, revenue in cursor.fetchall()
        ]

        return {
            "filters": {
                "region": region,
                "product": product
            },
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_order_value": avg_order_value,
            "top_product": {
                "name": top_product[0],
                "revenue": top_product[1]
            } if top_product else None,
            "top_region": {
                "name": top_region[0],
                "revenue": top_region[1]
            } if top_region else None,
            "monthly_revenue": monthly_revenue,
            "region_revenue": region_revenue,
            "product_revenue": product_revenue
        }

    finally:
        conn.close()



if __name__ == "__main__":
    print("Total Revenue:", get_total_revenue())
    print("Top Product:", get_top_product())
    print("Monthly Revenue:", get_monthly_revenue())
    print("Top Region:", get_top_region())
    print("Month Comparison:", compare_months("01", "02"))
