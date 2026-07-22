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


def get_user_recent_transactions(user_id, limit=5):
    """
    Return the user's most recent transactions.
    """

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
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
        ORDER BY e.date DESC, e.id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )

    rows = cursor.fetchall()

    return [dict(row) for row in rows]


def get_user_category_breakdown(user_id):
    """
    Return spending grouped by category.
    """

    db = get_db()
    cursor = db.cursor()

    # Total spent
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,),
    )

    total_spent = cursor.fetchone()["total"]

    # Spending per category
    cursor.execute(
        """
        SELECT
            c.name AS category,
            SUM(e.amount) AS amount
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.id
        WHERE e.user_id = ?
        GROUP BY c.name
        ORDER BY amount DESC
        """,
        (user_id,),
    )

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


def get_user_summary_stats(user_id):
    """
    Return summary statistics.
    """

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total_spent,
            COUNT(*) AS transaction_count
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,),
    )

    result = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            c.name,
            SUM(e.amount) AS total
        FROM expenses e
        JOIN categories c
            ON e.category_id = c.id
        WHERE e.user_id = ?
        GROUP BY c.name
        ORDER BY total DESC
        LIMIT 1
        """,
        (user_id,),
    )

    category = cursor.fetchone()

    return {
        "total_spent": result["total_spent"],
        "transaction_count": result["transaction_count"],
        "top_category": category["name"] if category else "—",
    }