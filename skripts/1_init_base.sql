--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Table: sku
CREATE TABLE IF NOT EXISTS public.sku
(
    uuid                   UUID,
    marketplace_id         INTEGER,
    product_id             BIGINT,
    title                  TEXT,
    description            TEXT,
    brand                  TEXT,
    seller_id              INTEGER,
    seller_name            TEXT,
    first_image_url        TEXT,
    category_id            INTEGER,
    category_lvl_1         TEXT,
    category_lvl_2         TEXT,
    category_lvl_3         TEXT,
    category_remaining     TEXT,
    features               JSONB,
    rating_count           INTEGER,
    rating_value           DOUBLE PRECISION,
    price_before_discounts REAL,
    discount               DOUBLE PRECISION,
    price_after_discounts  REAL,
    bonuses                INTEGER,
    sales                  INTEGER,
    inserted_at            TIMESTAMP DEFAULT NOW(),
    updated_at             TIMESTAMP DEFAULT NOW(),
    currency               TEXT,
    barcode                TEXT,
    similar_sku            UUID[]
);

-- Комментарии к колонкам
COMMENT ON COLUMN public.sku.uuid IS 'id товара в нашей бд';
COMMENT ON COLUMN public.sku.marketplace_id IS 'id маркетплейса';
COMMENT ON COLUMN public.sku.product_id IS 'id товара в маркетплейсе';
COMMENT ON COLUMN public.sku.title IS 'название товара';
COMMENT ON COLUMN public.sku.description IS 'описание товара';
COMMENT ON COLUMN public.sku.category_lvl_1 IS 'Первая часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Детям".';
COMMENT ON COLUMN public.sku.category_lvl_2 IS 'Вторая часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Электроника".';
COMMENT ON COLUMN public.sku.category_lvl_3 IS 'Третья часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Детская электроника".';
COMMENT ON COLUMN public.sku.category_remaining IS 'Остаток категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Игровая консоль/Игровые консоли и игры/Игровые консоли".';
COMMENT ON COLUMN public.sku.features IS 'Характеристики товара';
COMMENT ON COLUMN public.sku.rating_count IS 'Кол-во отзывов о товаре';
COMMENT ON COLUMN public.sku.rating_value IS 'Рейтинг товара (0-5)';
COMMENT ON COLUMN public.sku.barcode IS 'Штрихкод';

-- Создание индексов
CREATE INDEX sku_brand_index
    ON public.sku (brand);

CREATE UNIQUE INDEX sku_marketplace_id_sku_id_uindex
    ON public.sku (marketplace_id, product_id);

CREATE UNIQUE INDEX sku_uuid_uindex
    ON public.sku (uuid);
--
-- Data for Name: sku; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sku (uuid, marketplace_id, product_id, title, description, brand, seller_id, seller_name, first_image_url, category_id, category_lvl_1, category_lvl_2, category_lvl_3, category_remaining, features, rating_count, rating_value, price_before_discounts, discount, price_after_discounts, bonuses, sales, inserted_at, updated_at, currency, barcode, similar_sku) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

