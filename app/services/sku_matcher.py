import datetime
import logging

from db.db_client import DBClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import BulkIndexError


class Matcher:
    def __init__(self, db_uri, batch_size, es_params, el_schema, el_batch):
        self.db_uri = db_uri
        self.batch_size = batch_size
        self.es_params = es_params
        self.el_schema = el_schema
        self.el_batch = el_batch

    def get_connect(self):
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

    def match_skus(self, index_name):
        db_client = DBClient(self.db_uri)
        products = list(db_client.get_all_products(self.batch_size))
        updated_products = []
        # Подключаемся к Elastic
        result = self.get_connect()
        if result:
            for product_batch in self._chunked(products, self.el_batch):
                # Поиск похожих продуктов в Elasticsearch пачками
                similar_skus_map = self.search_similar_products_bulk(
                    products=product_batch,
                    max_results=5,
                    index_name=index_name,
                )
                # Обновляем поле similar_sku у каждого продукта
                for product in product_batch:
                    similar_skus = similar_skus_map.get(product.uuid, [])
                    product.similar_sku = similar_skus
                    updated_products.append(product.to_dict())
                if len(updated_products) >= (self.batch_size - self.el_batch):
                    logging.info(
                        f"save in db - {len(updated_products)} elements"
                    )
                    db_client.insert_or_update_products(updated_products)
                    updated_products = []
            # Если остались обновленные продукты, вставляем их
            if updated_products:
                db_client.insert_or_update_products(updated_products)
        self.es.close()

    def search_similar_products_bulk(
        self, products, max_results=5, index_name="products"
    ):
        """
        Выполняет поиск похожих продуктов для группы продуктов
         (batch) в Elasticsearch.
        Возвращает словарь с ключами UUID продуктов и
        значениями — списками similar_skus.
        """
        queries = []
        for product in products:
            queries.append({})  # Пустой объект метаданных для каждого запроса
            queries.append(
                {
                    "query": {
                        "more_like_this": {
                            "fields": ["title", "description"],
                            "like": [{"_id": product.uuid}],
                            "min_term_freq": 1,
                            "max_query_terms": 12,
                        }
                    },
                    "size": max_results,
                    "from": 0,
                    "sort": [],
                }
            )
        try:
            # Выполняем multi-search запрос пачками
            response = self.es.msearch(body=queries, index=index_name)
        except BulkIndexError as e:
            logging.error(f"Bulk indexing failed: {e.errors}")
            for error in e.errors:
                logging.error(f"Error in document: {error}")
        except Exception as e:
            logging.error(e)
            for error in e.errors:
                logging.error(f"Error in: {error}")
        similar_skus_map = {}
        # Обрабатываем результаты для каждого продукта в пачке
        for idx, result in enumerate(response["responses"]):
            hits = result["hits"]["hits"] if "hits" in result else []
            similar_skus = [hit["_source"]["uuid"] for hit in hits]
            similar_skus_map[products[idx].uuid] = similar_skus
        return similar_skus_map

    def _chunked(self, iterable, size):
        """Вспомогательная функция для разделения списка на части (батчи)"""
        for i in range(0, len(iterable), size):
            # fmt: off
            yield iterable[i: i + size]
            # fmt: on
