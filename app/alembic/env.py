import os
import asyncio
from logging.config import fileConfig
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

# 1) load your .env
load_dotenv()
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set in your environment")

# 2) grab Alembic Config and override the URL
alembic_cfg = context.config
alembic_cfg.set_main_option("sqlalchemy.url", database_url)

# 3) set up Python logging via the .ini
if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name)

# 4) point at your SQLAlchemy models’ metadata
#    e.g. from app.models import Base; target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' (SQL script) mode."""
    url = alembic_cfg.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_sync_migrations(connection: Connection) -> None:
    """Invoke migrations on a sync Connection inside an AsyncEngine."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def _run_migrations_online_async() -> None:
    """Helper: run migrations over an AsyncEngine."""
    connectable = async_engine_from_config(
        alembic_cfg.get_section(alembic_cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as conn:
        # run the sync migration logic in a “run_sync” block
        await conn.run_sync(_do_sync_migrations)

    # dispose the engine when done
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point: dispatch to the async helper."""
    asyncio.run(_run_migrations_online_async())


# Choose the right mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
