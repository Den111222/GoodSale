import uuid

from sqlalchemy import (
    ARRAY,
    JSON,
    REAL,
    TIMESTAMP,
    BigInteger,
    Column,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class SKU(Base):
    __tablename__ = "sku"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        comment="id товара в нашей бд",
    )
    marketplace_id = Column(Integer, nullable=False, comment="id маркетплейса")
    product_id = Column(
        BigInteger,
        nullable=False,
        unique=True,
        comment="id товара в маркетплейсе",
    )
    title = Column(Text, nullable=False, comment="название товара")
    description = Column(Text, comment="описание товара")
    brand = Column(Text, comment="бренд товара")
    seller_id = Column(Integer, comment="id продавца")
    seller_name = Column(Text, comment="название продавца")
    first_image_url = Column(Text, comment="URL первой картинки товара")
    category_id = Column(
        Integer, nullable=False, comment="id категории товара"
    )
    category_lvl_1 = Column(Text, comment="Первая часть категории товара")
    category_lvl_2 = Column(Text, comment="Вторая часть категории товара")
    category_lvl_3 = Column(Text, comment="Третья часть категории товара")
    category_remaining = Column(Text, comment="Остаток категории товара")
    features = Column(JSON, comment="Характеристики товара")
    rating_count = Column(Integer, comment="Количество отзывов о товаре")
    rating_value = Column(Float, comment="Рейтинг товара (0-5)")
    price_before_discounts = Column(REAL, comment="Цена до скидок")
    discount = Column(Float, comment="Скидка на товар")
    price_after_discounts = Column(REAL, comment="Цена после скидок")
    bonuses = Column(Integer, comment="Количество бонусов")
    sales = Column(Integer, comment="Количество продаж")
    inserted_at = Column(
        TIMESTAMP, server_default=func.now(), comment="Дата и время вставки"
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время обновления",
    )
    currency = Column(Text, comment="Валюта")
    barcode = Column(String, comment="Штрихкод товара")
    similar_sku = Column(
        ARRAY(UUID(as_uuid=True)), comment="Похожие товары (список UUID)"
    )

    def __repr__(self):
        return (
            f"<SKU(uuid={self.uuid}, "
            f"product_id={self.product_id}, "
            f"title={self.title})>"
        )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
