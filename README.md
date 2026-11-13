# 🌦️ dbt Weather Module

Pipeline **ELT** de estudo que coleta o clima atual de uma cidade na [API OpenWeather](https://openweathermap.org/api), carrega os dados brutos no **PostgreSQL** e transforma com **dbt** em camadas `staging` e `marts`.

```
API OpenWeather ──► data_pipeline.py ──► weather_data.city_weather (raw)
                                                   │
                                                   ▼
                              staging.stg_weather_report          (view)
                                                   │
                                                   ▼
                              staging.stg_weather_report_deduped  (view)
                                                   │
                                                   ▼
                              marts.mart_weather_report           (incremental)
```

## 🧱 Tecnologias

- **Python 3.12** + [uv](https://docs.astral.sh/uv/)
- `requests`, `psycopg2-binary`, `python-dotenv`
- **PostgreSQL**
- **dbt-core** + **dbt-postgres**

## 📂 Estrutura

```
.
├── pyproject.toml
└── weather/                      # projeto dbt
    ├── dbt_project.yml
    ├── scripts/
    │   ├── data_pipeline.py      # Extract + Load
    │   └── .env_example
    ├── macros/
    │   ├── convert_to_local.sql  # converte UTC para horário local
    │   └── get_custom_schema.sql # usa o nome de schema exato
    └── models/
        ├── sources/sources.yml
        ├── staging/
        │   ├── stg_weather_report.sql
        │   └── stg_weather_report_deduped.sql
        └── marts/
            └── mart_weather_report.sql
```

## ⚙️ Como funciona

### 1. Extract & Load (Python)
`weather/scripts/data_pipeline.py`:
- Busca o clima da cidade na API OpenWeather (`units=metric`)
- Cria o schema `weather_data` e a tabela `city_weather`, caso não existam
- Insere cidade, temperatura, descrição, velocidade do vento, horário da medição, horário de inserção e offset de fuso horário

### 2. Transform (dbt)
| Model | Materialização | Descrição |
|---|---|---|
| `stg_weather_report` | view | Converte `time` e `insert_at` para o horário local com a macro `convert_to_local` |
| `stg_weather_report_deduped` | view | Remove duplicados com `row_number()` por `id` |
| `mart_weather_report` | incremental | Tabela final; processa apenas registros novos (`unique_key = id`) |

Testes na source: `not_null` e `unique` em `id`; `not_null` em `city`, `temperature` e `time`.

## 🚀 Como rodar

### Pré-requisitos
- Python 3.12+ e `uv`
- PostgreSQL rodando
- Chave de API da [OpenWeather](https://home.openweathermap.org/api_keys)

### Passos

```bash
# 1. Instalar dependências
uv sync

# 2. Configurar variáveis de ambiente
cp weather/scripts/.env_example weather/scripts/.env
# preencha OPENWEATHER_API_KEY e as credenciais do Postgres

# 3. Coletar e carregar os dados
uv run python weather/scripts/data_pipeline.py

# 4. Rodar as transformações
cd weather
uv run dbt debug
uv run dbt run
uv run dbt test
```

### Profile do dbt
Crie `~/.dbt/profiles.yml` com um profile chamado `weather`:

```yaml
weather:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: <usuario>
      password: <senha>
      dbname: postgres
      schema: public
      threads: 1
```

## 📚 O que pratiquei

- Consumo de API REST e tratamento de erros em Python
- Carga em banco com queries parametrizadas
- `source()` e `ref()` no dbt e o grafo de dependências
- Materializações `view` e `incremental` (`is_incremental()`, `{{ this }}`)
- Macros Jinja e sobrescrita de `generate_schema_name`
- Testes genéricos do dbt


