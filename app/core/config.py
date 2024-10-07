import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

file_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=file_path)


file_path_xml = Path(__file__).resolve().parent.parent / "data/products.xml"
file_path_schema = (
    Path(__file__).resolve().parent.parent
    / "models/schemas/elstic_schema.json"
)


class Settings(BaseSettings):
    # XML
    xml_file_path: Path = file_path_xml

    # Postgres
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "127.0.0.1")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DSL: dict = {
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
    }
    POSTGRES_URI: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 6000))

    # Elasticsearch
    ELASTIC_HOST: str = os.getenv("ELASTIC_HOST", "127.0.0.1")
    ELASTIC_PORT: int = int(os.getenv("ELASTIC_PORT", 9200))
    ES_PARAMS: str = f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"
    EL_SCHEMA: str = str(os.getenv("EL_SCHEMA", file_path_schema))
    INDEX_NAME: str = os.getenv("INDEX_NAME", " products")
    EL_BATCH: int = int(os.getenv("BATCH_SIZE", 300))
    time_restart_etl: int = int(os.getenv("TIME_ETL_RESTART", 60))


settings = Settings()
