-- Views PostgreSQL para dashboard (Power BI / Databricks)

DROP VIEW IF EXISTS vw_headcount_mensal CASCADE;
CREATE VIEW vw_headcount_mensal AS
SELECT
    periodo_txt,
    COUNT(DISTINCT contratado) AS headcount
FROM funcionarios_mensal
WHERE bool_hc_colab_rd_clt IS TRUE
GROUP BY periodo_txt
ORDER BY periodo_txt;

DROP VIEW IF EXISTS vw_headcount_faixa_tenure CASCADE;
CREATE VIEW vw_headcount_faixa_tenure AS
SELECT
    periodo_txt,
    faixa_tempo_casa,
    COUNT(DISTINCT contratado) AS headcount
FROM funcionarios_mensal
WHERE bool_hc_colab_rd_clt IS TRUE
GROUP BY periodo_txt, faixa_tempo_casa
ORDER BY periodo_txt, faixa_tempo_casa;

DROP VIEW IF EXISTS vw_turnover_unidade CASCADE;
CREATE VIEW vw_turnover_unidade AS
SELECT
    periodo_txt,
    cod_sap,
    SUM(CASE WHEN bool_desligado IS TRUE THEN 1 ELSE 0 END) AS desligados,
    COUNT(DISTINCT CASE WHEN bool_hc_colab_rd_clt IS TRUE THEN contratado END) AS headcount,
    ROUND(
        SUM(CASE WHEN bool_desligado IS TRUE THEN 1 ELSE 0 END)::numeric
        / NULLIF(COUNT(DISTINCT CASE WHEN bool_hc_colab_rd_clt IS TRUE THEN contratado END), 0),
        4
    ) AS turnover
FROM funcionarios_mensal
WHERE cod_sap IS NOT NULL
GROUP BY periodo_txt, cod_sap
ORDER BY periodo_txt, cod_sap;

DROP VIEW IF EXISTS vw_desligados_gestor CASCADE;
CREATE VIEW vw_desligados_gestor AS
SELECT
    periodo_txt,
    COALESCE(matr_gestor::text, 'Sem gestor') AS gestor,
    COUNT(*) AS desligados
FROM funcionarios_mensal
WHERE bool_desligado IS TRUE
GROUP BY periodo_txt, COALESCE(matr_gestor::text, 'Sem gestor')
ORDER BY periodo_txt, desligados DESC;

DROP VIEW IF EXISTS vw_funcionarios_detalhe CASCADE;
CREATE VIEW vw_funcionarios_detalhe AS
SELECT
    contratado,
    periodo_txt,
    periodo_data,
    cargo,
    tipo_contrato,
    cod_sap,
    matr_gestor,
    id_situacao,
    data_admissao,
    data_rescisao,
    tempo_casa_anos,
    faixa_tempo_casa,
    tempo_desligamento_anos,
    motivo_desligamento,
    bool_hc_colab_rd_clt,
    bool_desligado,
    bool_admitidos,
    bool_reg_valido,
    flag_sem_gestor
FROM funcionarios_mensal;
