
from __future__ import annotations

from calendar import monthrange
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from config import PROJECT_ROOT, get_engine

RAW_CSV = PROJECT_ROOT / "data" / "raw" / "funcionarios.csv"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "postgres" / "01_schema.sql"
VIEWS_SQL = PROJECT_ROOT / "sql" / "postgres" / "02_views.sql"

COLUMN_RENAME = {
    "Id Local": "id_local",
    "Contratado": "contratado",
    "Id Centro de Custo": "id_centro_custo",
    "Id Cargo": "id_cargo",
    "Cargo": "cargo",
    "Id Situação": "id_situacao",
    "Data da Admissão": "data_admissao",
    "Data da Rescisão": "data_rescisao",
    "Id Sindicato": "id_sindicato",
    "Id Vínculo": "id_vinculo",
    "Desligamento": "motivo_desligamento",
    "Id Horário": "id_horario",
    "Id Centro de Custo Relativo": "id_centro_custo_relativo",
    "Idfolha": "id_folha",
    "Tipo de Contrato": "tipo_contrato",
    "Cód.sap": "cod_sap",
    "Matr gestor": "matr_gestor",
    "PeriodoTxt": "periodo_txt",
    "BoolHcColabRdClt": "bool_hc_colab_rd_clt",
    "BoolDesligado": "bool_desligado",
    "BoolAdmitidos": "bool_admitidos",
    "BoolRegValido": "bool_reg_valido",
    "BoolAtividade": "bool_atividade",
    "BoolHcColabRd": "bool_hc_colab_rd",
    "BoolRotatividade": "bool_rotatividade",
    "BoolTransferencia": "bool_transferencia",
    "Numero_vaga": "numero_vaga",
    "periodo": "periodo",
}

BOOL_COLUMNS = [
    "bool_hc_colab_rd_clt",
    "bool_desligado",
    "bool_admitidos",
    "bool_reg_valido",
    "bool_atividade",
    "bool_hc_colab_rd",
    "bool_rotatividade",
    "bool_transferencia",
]

INTEGER_COLUMNS = [
    "id_local",
    "contratado",
    "id_centro_custo",
    "id_cargo",
    "id_situacao",
    "id_sindicato",
    "id_vinculo",
    "id_horario",
    "id_centro_custo_relativo",
    "id_folha",
    "matr_gestor",
    "periodo_txt",
    "numero_vaga",
]


def periodo_to_last_day(periodo_txt: int) -> date:
    year = periodo_txt // 100
    month = periodo_txt % 100
    return date(year, month, monthrange(year, month)[1])


def assign_tenure_band(years: float) -> str:
    if pd.isna(years):
        return "Indefinido"
    if years < 0.25:
        return "Até 3 meses"
    if years < 0.5:
        return "3 a 6 meses"
    if years < 1.0:
        return "6 a 12 meses"
    if years < 2.0:
        return "1 a 2 anos"
    if years < 5.0:
        return "2 a 5 anos"
    return "Mais de 5 anos"


def parse_bool_series(series: pd.Series) -> pd.Series:
    mapping = {"True": True, "False": False, True: True, False: False}
    return series.map(mapping).astype("boolean")


def load_raw() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {RAW_CSV}")
    return pd.read_csv(RAW_CSV, low_memory=False)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    initial_rows = len(df)
    df = df.rename(columns=COLUMN_RENAME)
    df = df.dropna(subset=["contratado", "periodo_txt"])
    print(f"Linhas removidas (sem contratado/periodo): {initial_rows - len(df)}")

    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = parse_bool_series(df[col])

    for col in INTEGER_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["periodo_txt"] = df["periodo_txt"].astype("Int64")
    df["data_admissao"] = pd.to_datetime(df["data_admissao"], errors="coerce")
    df["data_rescisao"] = pd.to_datetime(df["data_rescisao"], errors="coerce")

    df.loc[df["matr_gestor"] == 0, "matr_gestor"] = pd.NA
    df["flag_sem_gestor"] = df["matr_gestor"].isna()

    df["periodo_data"] = pd.to_datetime(
        df["periodo_txt"].apply(
            lambda p: periodo_to_last_day(int(p)) if pd.notna(p) else pd.NaT
        )
    )

    df["tempo_casa_anos"] = (
        (df["periodo_data"] - df["data_admissao"]).dt.days / 365.25
    )

    df["tempo_desligamento_anos"] = pd.NA
    mask_desligado = df["bool_desligado"] == True
    df.loc[mask_desligado, "tempo_desligamento_anos"] = (
        (
            df.loc[mask_desligado, "data_rescisao"]
            - df.loc[mask_desligado, "data_admissao"]
        ).dt.days
        / 365.25
    )

    df["faixa_tempo_casa"] = df["tempo_casa_anos"].apply(assign_tenure_band)

    
    for col in BOOL_COLUMNS + ["flag_sem_gestor"]:
        df[col] = df[col].astype("boolean")

    return df


def run_sql_file(engine, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))


def load_to_postgres(df: pd.DataFrame) -> None:
    engine = get_engine()
    run_sql_file(engine, SCHEMA_SQL)
    df.to_sql(
        "funcionarios_mensal",
        engine,
        index=False,
        if_exists="append",
        method="multi",
        chunksize=1000,
    )
    print(f"Dados carregados: {len(df)} linhas")


def apply_views() -> None:
    engine = get_engine()
    run_sql_file(engine, VIEWS_SQL)
    print("Views SQL aplicadas.")


def print_validation() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        hc_dez = conn.execute(
            text(
                "SELECT headcount FROM vw_headcount_mensal WHERE periodo_txt = 201912"
            )
        ).scalar()
        total_desligados = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM funcionarios_mensal WHERE bool_desligado IS TRUE
                """
            )
        ).scalar()
        max_turnover = conn.execute(
            text("SELECT MAX(turnover) FROM vw_turnover_unidade")
        ).scalar()

    print("\n--- Validação ---")
    print(f"Headcount dez/2019: {hc_dez}")
    print(f"Total desligados: {total_desligados}")
    print(f"Turnover máximo por unidade/mês: {max_turnover}")


def main() -> None:
    print("Iniciando ETL People Analytics (PostgreSQL)...")
    df_raw = load_raw()
    print(f"Linhas lidas: {len(df_raw)}")

    df_clean = transform(df_raw)
    load_to_postgres(df_clean)
    apply_views()
    print_validation()
    print("ETL concluído.")


if __name__ == "__main__":
    main()
