{{ config(
  materialized='incremental',
  unique_key='id'
)
}}

with source as (
  select *
  from {{ ref('stg_weather_report_deduped')}}
  {% if is_incremental() %}
    where inserted_at_local > (select max(inserted_at_local) from {{ this }})
    {% endif %}
)
select
  id,
  city,
  temperature,
  weather_description,
  wind_speed,
  weather_time_local,
  inserted_at_local
from source
