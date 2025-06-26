REVIEW_INSERT = """
    INSERT INTO review (review, sentiment, probability, date)
    VALUES (%s, %s, %s, NOW())
"""

REVIEW_UPDATE = """
    UPDATE review
    SET review = %s, date = NOW()
    WHERE id = %s
"""

REVIEW_DELETE = """
    DELETE FROM review
    WHERE id = %s
"""

GET_REVIEW_BY_KEYWORD = """
    SELECT id, review, sentiment, probability, date
    FROM review
    WHERE review LIKE %s
    ORDER BY date DESC
    LIMIT 100
"""

GET_SENTIMENT_STATS = """
    SELECT sentiment, COUNT(*) as count
    FROM review
    GROUP BY sentiment
"""

GET_WEEKLY_STATS = """
    SELECT 
        DATE_FORMAT(date, '%%Y-%%u주차') AS week,
        COUNT(*) AS count
    FROM review
    GROUP BY week
    ORDER BY week DESC
"""

GET_MONTHLY_SENTIMENT_STATS = """
    SELECT 
        DATE_FORMAT(date, '%%Y-%%m') AS month,
        sentiment,
        COUNT(*) as count
    FROM review
    GROUP BY month, sentiment
    ORDER BY month DESC
"""

GET_MONTHLY_REVIEW_STATS = """
    SELECT 
        DATE_FORMAT(date, '%%Y-%%m') AS month,
        COUNT(*) as count
    FROM review
    GROUP BY month
    ORDER BY month DESC
"""

FEEDBACK_INSERT = """
    INSERT INTO feedback (review, original_sentiment, corrected_sentiment, feedback_type, probability)
    VALUES (%s, %s, %s, %s, %s)
"""

FEEDBACK_SELECT_RECENT = """
    SELECT id, review, original_sentiment, corrected_sentiment, feedback_type, probability, created_at
    FROM feedback
    ORDER BY created_at DESC
    LIMIT %s
"""

GET_POSITIVE_REVIEWS = """
    SELECT review
    FROM review
    WHERE sentiment = 1
    ORDER BY date DESC
    LIMIT 1000
"""

GET_NEGATIVE_REVIEWS = """
    SELECT review
    FROM review
    WHERE sentiment = 0
    ORDER BY date DESC
    LIMIT 1000
"""

GET_ALL_REVIEWS = """
    SELECT review
    FROM review
    ORDER BY date DESC
    LIMIT 500
"""


MODEL_HISTORY_INSERT = """
    INSERT INTO model_history (model_name, switched_at)
    VALUES (%s, NOW())
"""
