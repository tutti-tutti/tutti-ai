from contextlib import contextmanager
from app.db.connection import get_db_connection

@contextmanager
def with_db_cursor(commit: bool = False):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
