import logging

from models.db.models import SKU
from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker


class DBClient:
    def __init__(self, db_uri):
        try:
            self.engine = create_engine(db_uri, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            logging.info("Successfully connected to the database.")
        except OperationalError as e:
            logging.error(f"Error connecting to the database: {e}")

    def insert_or_update_products(self, products_data: list[dict]):
        with self.Session() as session:
            try:
                stmt = insert(SKU).values(products_data)
                update_dict = {
                    column.name: stmt.excluded[column.name]
                    for column in SKU.__table__.columns
                    if column.name not in ["uuid", "inserted_at", "updated_at"]
                }
                stmt = stmt.on_conflict_do_update(
                    index_elements=["marketplace_id", "product_id"],
                    set_=update_dict,
                )
                session.execute(stmt)
                session.commit()
            except Exception as e:
                logging.error(f"Failed to upsert products: {e}")
                session.rollback()

    def get_all_products(self, batch_size: int):
        with self.Session() as session:
            query = select(SKU)
            for batch in (
                session.execute(query.execution_options(stream_results=True))
                .scalars()
                .yield_per(batch_size)
            ):
                yield batch
