# People Analytics — Case Técnico



## Visão Geral



Este projeto tem como objetivo desenvolver uma solução analítica de People Analytics para acompanhamento de indicadores estratégicos de colaboradores.



A proposta foi transformar uma base operacional de RH em um modelo estruturado de análise, passando pelas etapas de tratamento, modelagem e visualização dos dados.



Fluxo desenvolvido:



- Tratamento e preparação dos dados com Python

- Transformação utilizando Pandas

- Estruturação da camada de dados

- Criação de consultas SQL para análise

- Construção do dashboard em Power BI



O projeto foi desenvolvido considerando boas práticas de organização, rastreabilidade dos dados e separação entre preparação dos dados e camada de visualização.



---



# Arquitetura do Projeto



Fluxo dos dados:





Base RH (.csv)



&#x20;       ↓



ETL Python



&#x20;       ↓



Tratamento Pandas



&#x20;       ↓



Banco de Dados



&#x20;       ↓



Consultas SQL



&#x20;       ↓



Power BI Dashboard





---



# Estrutura do Projeto





case-rd/



├── data/

│   ├── raw/

│   │   └── funcionarios.csv

│   │

│   └── processed/

│       └── people_analytics.db

│

├── sql/

│   ├── 01_schema.sql

│   └── 02_views.sql

│

├── src/

│   ├── config.py

│   ├── etl.py

│   └── requirements.txt

│

├── dashboard.pbix

└── README.md





---



# Pipeline de Dados





## 1. Base Original



Arquivo:



`data/raw/funcionarios.csv`



Contém os dados originais dos colaboradores utilizados para criação dos indicadores.



A base contém informações relacionadas a:



- Dados cadastrais

- Unidade

- Cargo

- Gestor

- Datas de admissão e desligamento

- Status do colaborador

- Informações organizacionais





---



# 2. Processo ETL — Python



Arquivo:



`src/etl.py`



Responsável pelo processo de extração, transformação e carga dos dados.





Principais etapas realizadas:



- Leitura da base original

- Padronização dos campos

- Tratamento dos tipos de dados

- Conversão de datas

- Criação de campos calculados

- Preparação da tabela analítica para consumo





Exemplos de campos derivados:



- Tempo de casa

- Faixas de tempo de empresa

- Indicadores de status do colaborador





A saída desse processo gera a camada tratada:



`data/processed/people_analytics.db`





---



# 3. Modelagem SQL





## Schema



Arquivo:



`sql/01_schema.sql`



Responsável pela definição da estrutura da tabela principal utilizada no projeto.





---



## Views Analíticas



Arquivo:



`sql/02_views.sql`





Responsável pela criação das consultas utilizadas para responder perguntas de negócio e alimentar as análises.





As views foram estruturadas para facilitar o consumo dos indicadores no Power BI.





---



# Indicadores Construídos





## Headcount



Objetivo:



Acompanhar a quantidade de colaboradores ativos e sua distribuição.





Permite análises como:



- Evolução do quadro

- Distribuição por unidade

- Perfil dos colaboradores





---



## Tempo de Casa (Tenure)



Objetivo:



Analisar a composição do headcount conforme tempo de empresa.





A análise permite identificar a distribuição dos colaboradores por faixas como:



- Menos de 1 ano

- Entre 1 e 2 anos

- Acima de 2 anos





Esse indicador apoia análises relacionadas ao perfil da população atual e maturidade do quadro de colaboradores.





---



## Turnover



Objetivo:



Avaliar movimentações e desligamentos de colaboradores.





Permite acompanhar:



- Rotatividade

- Distribuição dos desligamentos

- Possíveis pontos de atenção por área ou unidade





---



## Qualidade dos Dados



Durante a análise foi identificado um volume relevante de colaboradores desligados sem gestor informado no cadastro.



Esse ponto representa uma oportunidade de melhoria em:



- Governança de dados de RH

- Padronização cadastral

- Qualidade das informações utilizadas nos indicadores





---



# Dashboard Power BI



Arquivo:



`dashboard.pbix`





O dashboard consolida as informações tratadas e disponibiliza uma visão analítica dos principais indicadores de pessoas.





Principais análises:



- Headcount

- Distribuição por tempo de casa

- Turnover

- Unidade

- Perfil dos colaboradores

- Qualidade cadastral





---



# Tecnologias Utilizadas



- Python

- Pandas

- SQL

- PostgreSQL

- Power BI

- Power Query

- Figma

- Canva





---



# Objetivo Final



Construir uma solução de People Analytics baseada em dados, permitindo transformar informações operacionais de RH em indicadores estratégicos para apoiar a tomada de decisão.

