import logging
from typing import Any

import lxml.etree as ET
from core.config import settings
from db.db_client import DBClient
from sqlalchemy.exc import SQLAlchemyError


class ETL_XML:
    def __init__(self, file_path: str, db_client: DBClient):
        self.file_path = file_path
        self.extractor = Extract()
        self.transformer = Transform()
        self.loader = Load(db_client)

    def etl_process(self) -> None:
        parsed_data = []
        count_parsed_data = 0
        with open(self.file_path, "rb") as f:
            context, categories, shop_name = self.extractor.extract_data(f)
            if context is not None:
                for event, elem in context:
                    product_data = self.transformer.transform_product_element(
                        elem, categories, shop_name
                    )
                    if product_data:
                        parsed_data.append(product_data)
                        if count_parsed_data < settings.BATCH_SIZE:
                            count_parsed_data += 1
                        else:
                            self.loader.load_data(parsed_data)
                            parsed_data = []
                            count_parsed_data = 0
                    elem.clear()
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]
                self.loader.load_data(parsed_data)


class Extract:
    def extract_data(
        self, xml_file
    ) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]], str]:
        try:
            categories = self.parse_categories_from_xml(xml_file)
            xml_file.seek(0)
            tree = ET.iterparse(
                xml_file, events=("end",), tag="shop", recover=True
            )
            shop_name = [
                elem.findtext("name", default=0) for ev, elem in tree
            ][0]
            xml_file.seek(0)  # Сбрасываем указатель в начало файла
            context = ET.iterparse(
                xml_file, events=("end",), tag="offer", recover=True
            )
            return context, categories, shop_name
        except Exception as e:
            logging.error(f"Error extracting data from XML: {e}")
            return None, {}, ""

    def parse_categories_from_xml(self, xml_file) -> dict[int, dict[str, Any]]:
        categories = {}
        try:
            context = ET.iterparse(
                xml_file, events=("start", "end"), recover=True
            )
            _, root = next(context)  # Пропускаем корневой элемент
            for event, elem in context:
                if event == "end" and elem.tag == "category":
                    category_id = int(elem.attrib["id"])
                    parent_id = int(elem.attrib.get("parentId", 0))
                    category_name = elem.text.strip()
                    categories[category_id] = {
                        "name": category_name,
                        "parent_id": parent_id,
                    }
                    elem.clear()
        except Exception as e:
            logging.error(f"Error parsing categories: {e}")
        return categories


class Transform:
    def __init__(self):
        pass

    def transform_product_element(
        self,
        elem: ET.Element,
        categories: dict[int, dict[str, Any]],
        shop_name: str,
    ) -> dict[str, Any]:
        try:
            category_id = int(elem.findtext("categoryId", default=0))
            (
                category_lvl_1,
                category_lvl_2,
                category_lvl_3,
            ), category_remaining = self.get_category_levels(
                category_id, categories
            )
            features = {}
            for param in elem.findall("param"):
                param_name = param.attrib.get("name")
                param_value = param.text
                if param_name and param_value:
                    features[param_name] = param_value.strip()
            product = {
                "marketplace_id": 1,
                "product_id": int(elem.attrib.get("id")),
                "title": elem.findtext("name", default="").strip(),
                "description": elem.findtext(
                    "description", default=""
                ).strip(),
                "brand": elem.findtext("vendor", default="").strip(),
                "seller_id": None,
                "seller_name": shop_name,
                "first_image_url": elem.findtext(
                    "picture", default=""
                ).strip(),
                "category_id": category_id,
                "category_lvl_1": category_lvl_1,
                "category_lvl_2": category_lvl_2,
                "category_lvl_3": category_lvl_3,
                "category_remaining": category_remaining,
                "features": features,
                "rating_count": None,
                "rating_value": None,
                "price_before_discounts": float(
                    elem.findtext("oldprice", default=0)
                ),
                "discount": (
                    (
                        float(elem.findtext("oldprice", default=0))
                        - float(elem.findtext("price", default=0))
                    )
                    if float(elem.findtext("oldprice", default=0))
                    > float(elem.findtext("price", default=0))
                    else None
                ),
                "price_after_discounts": float(
                    elem.findtext("price", default=0)
                ),
                "bonuses": None,
                "sales": None,
                "currency": elem.findtext("currencyId", default="").strip(),
                "barcode": int(elem.findtext("barcode", default=0)),
                "similar_sku": [],
            }
            return product
        except ValueError as ve:
            logging.error(f"Error converting values: {ve}")
            return {}
        except Exception as e:
            logging.error(f"Error parsing product element: {e}")
            return {}

    def get_category_levels(
        self, category_id: int, categories: dict[int, dict[str, Any]]
    ) -> list[str]:
        levels = ["", "", ""]
        remaining = []
        current_id = category_id
        level = 2

        while current_id:
            category = categories.get(current_id)
            if category:
                if level >= 0:
                    levels[level] = category["name"]
                else:
                    remaining.append(category["name"])
                current_id = category.get("parent_id")
                level -= 1
            else:
                break

        category_remaining = " > ".join(remaining[::-1])
        return levels, category_remaining


class Load:
    def __init__(self, db_client: DBClient):
        self.db_client = db_client

    def load_data(self, parsed_data: list[dict[str, Any]]) -> None:
        try:
            self.db_client.insert_or_update_products(parsed_data)
        except SQLAlchemyError as e:
            logging.error(f"Failed to insert product: {e}")
        except Exception as e:
            logging.error(f"Error loading data to DB: {e}")
