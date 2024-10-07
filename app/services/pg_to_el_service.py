import datetime
import json
import logging
from pathlib import Path

from db.db_client import DBClient
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from elasticsearch.helpers import BulkIndexError, bulk
from models.db.models import SKU


class PostgresExtractor:
    def __init__(self, db_uri: str, batch_size: int):
        self.db_uri = db_uri
        self.batch_size = batch_size

    def get_data(self) -> list[SKU]:
        db_client = DBClient(self.db_uri)
        data = [sku for sku in db_client.get_all_products(self.batch_size)]
        return data


class DataTransform:
    def transform_data(self, data: any) -> list[SKU]:
        return data


class ElasticsearchLoader:
    def __init__(self, es_params: dict, el_schema: Path):
        self.es_params = es_params
        self.el_schema = el_schema

    # @backoff()
    def get_connect(self) -> bool | None:
        self.es = Elasticsearch([self.es_params])
        if self.es.ping():
            logging.info(
                f"Successful connection to "
                f"Elasticsearch {datetime.datetime.now()}"
            )
            return True
        else:
            logging.info("Elasticsearch is not available")
            raise ConnectionError("Failed to ping Elasticsearch")

    def load_data_to_es(self, el_batch, es_data, index_name):
        result = self.get_connect()
        if result:
            try:
                with open(Path(self.el_schema), "r") as file:
                    index_settings_and_mapping = json.load(file)
            except Exception as e:
                logging.error(e)
            # Creating an index with settings
            # Создание индекса с настройками
            if not self.es.indices.exists(index=index_name):
                self.es.indices.create(
                    index=index_name,
                    settings=index_settings_and_mapping["settings"],
                    mappings=index_settings_and_mapping["mappings"],
                )
            # Adding data
            # Добавление данных
            self.adding_data(es_data, index_name, el_batch)
        else:
            return "Not finish"
        self.close_connections()
        return "Finish"

    def adding_data(self, es_data, index_name, el_batch):
        if es_data:
            # Division into bundles by el_batch
            # Деление на пачки по размуру el_batch
            # fmt: off
            data_batches = [
                es_data[i: i + el_batch]
                for i in range(0, len(es_data), el_batch)
            ]
            # fmt: on
            # Send each packet of data separately
            # Отправляем каждую пачку данных отдельно
            for data_batch in data_batches:
                try:
                    success, failed = bulk(
                        client=self.es,
                        actions=self.doc_generator(data_batch, index_name),
                        stats_only=True,
                    )
                    if not success:
                        logging.error(
                            "Error when creating an elastic "
                            "index or updating data."
                        )
                except BulkIndexError as e:
                    logging.error(f"Bulk indexing failed: {e.errors}")
                    for error in e.errors:
                        logging.error(f"Error in document: {error}")
        else:
            logging.info(f"No data to add at elastic index {index_name}.")

    def doc_generator(self, data, index_name):
        documents = []
        for doc in data:
            # TODO сделать pydantic схему для документа
            document = {
                "_index": index_name,
                "_id": str(doc.uuid),
                "_op_type": "index",
                "_source": doc.to_dict(),
            }
            documents.append(document)
        return documents

    def search_product(self, products, batch_size):
        result = self.get_connect()
        if result:
            load_data = []
            check = {}
            # Разбиваем список продуктов на батчи
            for i in range(0, len(products), batch_size):
                # Собираем UUID текущего батча
                # fmt: off
                batch = products[i: i + batch_size]
                # fmt: on
                product_uuids = [str(product.uuid) for product in batch]
                query = {
                    "query": {"terms": {"uuid": product_uuids}},
                    "size": batch_size,
                }
                response = self.es.search(index="products", body=query)
                # Получаем найденные UUID из результатов поиска
                found_uuids = {
                    hit["_source"]["uuid"] for hit in response["hits"]["hits"]
                }
                for product in product_uuids:
                    if product not in found_uuids:
                        check[product] = False
                        load_data.append(
                            [
                                prod
                                for prod in batch
                                if str(prod.uuid) == product
                            ][0]
                        )
                    else:
                        check[product] = True
            self.close_connections()
            return check, load_data

    def close_connections(self):
        self.es.close()
