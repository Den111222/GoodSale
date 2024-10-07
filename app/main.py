import datetime
import logging

from core.config import settings
from db.db_client import DBClient
from services.pg_to_el_service import (
    DataTransform,
    ElasticsearchLoader,
    PostgresExtractor,
)
from services.sku_matcher import Matcher
from services.xml_to_pg_service import ETL_XML

es_params = settings.ES_PARAMS
el_schema = settings.EL_SCHEMA


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("elastic_transport.transport").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)


def timing(action, proccess_name, args):
    t0 = datetime.datetime.now()
    logging.info(f"Start process {proccess_name}: {datetime.datetime.now()}")
    if args:
        result = action(*args)
    else:
        result = action()
    t1 = datetime.datetime.now() - t0
    logging.info(
        f"End process {proccess_name}: {datetime.datetime.now()}, "
        f"duration: {t1}"
    )
    return result


def start_etl_process():
    logging.info(f"Starting a data entry operation {datetime.datetime.now()}")
    start_etl_xml_to_pg(settings.xml_file_path, settings.POSTGRES_URI)
    elastic_test_connection()
    start_etl_pg_to_es()
    find_similar_and_add_to_base()
    logging.info(f"Finished a data entry operation {datetime.datetime.now()}")


def start_etl_xml_to_pg(xml_file_path, db_uri):
    db_client = DBClient(db_uri)
    etl_service = ETL_XML(xml_file_path, db_client)
    timing(etl_service.etl_process, "1. Parse_xml_and_save_db", [])


def elastic_test_connection():
    el_s_test = ElasticsearchLoader(es_params, el_schema)
    el_s_test_connect = el_s_test.get_connect()
    if el_s_test_connect:
        logging.info(
            f"The test connection to elasticsearch "
            f"was successful {datetime.datetime.now()}"
        )
        el_s_test.close_connections()


def start_etl_pg_to_es():
    pg_ex = PostgresExtractor(settings.POSTGRES_URI, settings.BATCH_SIZE)
    data_from_pg = timing(pg_ex.get_data, "2. Get data collection from db", [])
    if data_from_pg:
        transform_obj = DataTransform()
        transformed_data_to_es = timing(
            transform_obj.transform_data,
            "3. Data transformation",
            [data_from_pg],
        )
        etl_load(transformed_data_to_es)
        return True
    else:
        logging.info("No data in DB")


def etl_load(transformed_data_to_es):
    el_l = ElasticsearchLoader(es_params, settings.EL_SCHEMA)
    result = timing(
        el_l.load_data_to_es,
        "4. Data loading into elastic",
        [settings.EL_BATCH, transformed_data_to_es, settings.INDEX_NAME],
    )
    if result == "Finish":
        logging.info(
            f"The entry of all data into elastic was successful "
            f"in {datetime.datetime.now()}"
        )
    else:
        logging.info(
            "Data recording in elastic is interrupted "
            "in the middle of the process and will "
            "be corrected on restart"
        )


def find_similar_and_add_to_base():
    matcher = Matcher(
        db_uri=settings.POSTGRES_URI,
        batch_size=settings.BATCH_SIZE,
        es_params=es_params,
        el_schema=settings.EL_SCHEMA,
        el_batch=settings.EL_BATCH,
    )
    timing(
        matcher.match_skus,
        "5. Match similar and save db",
        [settings.INDEX_NAME],
    )


def main():
    configure_logging()
    start_etl_process()


if __name__ == "__main__":
    main()
