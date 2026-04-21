from __future__ import annotations

from pathlib import Path
from sqlalchemy import text


def _run_sql(conn, sql: str) -> None:
    if conn.dialect.name == "sqlite":
        raw = conn.connection
        raw.executescript(sql)
    else:
        for statement in [s.strip() for s in sql.split(";") if s.strip()]:
            conn.execute(text(statement))


def apply_migrations(engine) -> None:
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    sql_files = sorted(migrations_dir.glob("*.sql"))

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        applied = {
            row[0]
            for row in conn.execute(text("SELECT version FROM schema_migrations"))
        }

        for sql_path in sql_files:
            version = sql_path.name
            if version in applied:
                continue
            sql = sql_path.read_text(encoding="utf-8")
            _run_sql(conn, sql)
            conn.execute(
                text("INSERT INTO schema_migrations(version) VALUES (:v)"),
                {"v": version},
            )
