"""Configuração de conexão com o banco."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DATABASE_URL = (
    "sua_url_aqui"
)


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine() -> Engine:
    return create_engine(get_database_url(), future=True)
