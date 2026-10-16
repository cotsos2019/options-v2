"""
db.py — Postgres helpers for Options Dashboard v2
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _conn():
    """Create a new connection to Postgres."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "options_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        connect_timeout=10,
    )


def init_db():
    """Create tables if they don't exist."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id          SERIAL PRIMARY KEY,
                name        VARCHAR(200) NOT NULL,
                symbol      VARCHAR(20) NOT NULL,
                legs        JSONB NOT NULL,
                created_at  TIMESTAMP DEFAULT NOW(),
                updated_at  TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_strategies_created
            ON strategies (created_at DESC);
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[db] init_db OK")
        return True
    except Exception as e:
        print(f"[db] init_db error: {e}")
        return False


def save_strategy(name, symbol, legs):
    """Insert a new strategy. Returns the new id, or None on error."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO strategies (name, symbol, legs)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (name.strip(), symbol, json.dumps(legs)))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"[db] saved strategy id={new_id} name={name}")
        return new_id
    except Exception as e:
        print(f"[db] save_strategy error: {e}")
        return None


def load_strategies():
    """Return all strategies, newest first."""
    try:
        conn = _conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, name, symbol, legs, created_at, updated_at
            FROM strategies
            ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for r in rows:
            result.append({
                "id": str(r["id"]),
                "name": r["name"],
                "symbol": r["symbol"],
                "legs": r["legs"] if isinstance(r["legs"], list) else json.loads(r["legs"]),
                "saved_at": r["created_at"].strftime("%Y-%m-%d %H:%M") if r["created_at"] else "",
            })
        return result
    except Exception as e:
        print(f"[db] load_strategies error: {e}")
        return []


def delete_strategy(strategy_id):
    """Delete a strategy by id."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM strategies WHERE id = %s;", (int(strategy_id),))
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        print(f"[db] deleted strategy id={strategy_id} (rows={deleted})")
        return deleted > 0
    except Exception as e:
        print(f"[db] delete_strategy error: {e}")
        return False


def count_strategies():
    """Return the number of saved strategies."""
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM strategies;")
        n = cur.fetchone()[0]
        cur.close()
        conn.close()
        return n
    except Exception as e:
        print(f"[db] count_strategies error: {e}")
        return 0