from .db import get_db


def get_user_by_id(user_id):
    """
    Get user information by user ID.
    """

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    return dict(row) if row else None


def get_user_recent_transactions(user_id, limit=5, start_date=None, end_date=None):
    """
    Return the user's most recent transactions.
    Optional start_date and end_date filter results to the given date range (inclusive).
    Dates must be in 'YYYY-MM-DD' format.
    """

    db = get_db()
    cursor = db.cursor()

    query = """
        SELECT
            e.id,
            e.date,
            e.description,
            c.name AS category,
            e.amount
        FROM expenses e
        LEFT JOIN categories c
            ON e.category_id = c.id
        WHERE e.user_id = ?
    """
    params = [user_id]

    # Add date filtering if both dates are provided and valid
    if start_date and end_date:
        # Simple validation: check for YYYY-MM-DD format (basic)
        if len(start_date) == 10 and start_date[4] == '-' and start_date[7] == '-' and \
           len(end_date) == 10 and end_date[4] == '-' and end_date[7] == '-':
            query += " AND e.date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

    query += " ORDER BY e.date DESC, e.id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    rows = cursor.fetchall()

    return [dict(row) for row in rows]


def get_user_category_breakdown(user_id, start_date=None, end_date=None):
    """
    Return spending grouped by category.
    Optional start_date and end_date filter results to the given date range (inclusive).
    Dates must be in 'YYYY-MM-DD' format.
    """

    db = get_db()
    cursor = db.cursor()

    # Base query for total spent with optional date filter
    total_query = """
        SELECT
            COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
    """
    total_params = [user_id]

    # Base query for category breakdown with optional date filter
    category_query = """
        SELECT
            c.name AS category,
            SUM(e.amount) AS amount
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.id
        WHERE e.user_id = ?
    """
    category_params = [user_id]

    # Add date filtering if both dates are provided and valid
    if start_date and end_date:
        # Simple validation: check for YYYY-MM-DD format (basic)
        if len(start_date) == 10 and start_date[4] == '-' and start_date[7] == '-' and \
           len(end_date) == 10 and end_date[4] == '-' and end_date[7] == '-':
            date_condition = " AND e.date BETWEEN ? AND ?"
            total_query += date_condition
            category_query += date_condition
            total_params.extend([start_date, end_date])
            category_params.extend([start_date, end_date])

    # Total spent
    cursor.execute(total_query, tuple(total_params))
    total_spent = cursor.fetchone()["total"]

    # Spending per category
    cursor.execute(category_query, tuple(category_params))
    rows = cursor.fetchall()

    breakdown = []

    for row in rows:
        amount = row["amount"]

        percentage = (
            round((amount / total_spent) * 100)
            if total_spent > 0
            else 0
        )

        breakdown.append({
            "category": row["category"],
            "amount": amount,
            "percentage": percentage,
        })

    # Ensure percentages total exactly 100%
    if breakdown:
        total_percentage = sum(item["percentage"] for item in breakdown)

        if total_percentage != 100:
            breakdown[0]["percentage"] += (100 - total_percentage)

    return breakdown


def get_user_summary_stats(user_id, start_date=None, end_date=None):
    """
    Return summary statistics.
    Optional start_date and end_date filter results to the given date range (inclusive).
    Dates must be in 'YYYY-MM-DD' format.
    """

    db = get_db()
    cursor = db.cursor()

    # Base query for total spent and transaction count with optional date filter
    stats_query = """
        SELECT
            COALESCE(SUM(amount), 0) AS total_spent,
            COUNT(*) AS transaction_count
        FROM expenses
        WHERE user_id = ?
    """
    stats_params = [user_id]

    # Base query for top category with optional date filter
    top_category_query = """
        SELECT
            c.name,
            SUM(e.amount) AS total
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.id
        WHERE e.user_id = ?
    """
    top_category_params = [user_id]

    # Add date filtering if both dates are provided and valid
    if start_date and end_date:
        # Simple validation: check for YYYY-MM-DD format (basic)
        if len(start_date) == 10 and start_date[4] == '-' and start_date[7] == '-' and \
           len(end_date) == 10 and end_date[4] == '-' and end_date[7] == '-':
            date_condition = " AND e.date BETWEEN ? AND ?"
            stats_query += date_condition
            top_category_query += date_condition
            stats_params.extend([start_date, end_date])
            top_category_params.extend([start_date, end_date])

    # Total spent and transaction count
    cursor.execute(stats_query, tuple(stats_params))
    result = cursor.fetchone()

    # Top category
    cursor.execute(top_category_query + " GROUP BY c.name ORDER BY total DESC LIMIT 1", tuple(top_category_params))
    category = cursor.fetchone()

    return {
        "total_spent": result["total_spent"],
        "transaction_count": result["transaction_count"],
        "top_category": category["name"] if category else "—",
    }