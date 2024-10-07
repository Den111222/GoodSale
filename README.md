# Goodsale Python Test Task

### Описание:

Нужно написать сервис, который будет:

1. Открывать [файл с выгрузкой](http://export.admitad.com/ru/webmaster/websites/777011/products/export_adv_products/?user=bloggers_style&code=uzztv9z1ss&feed_id=21908&format=xml) по маркетплейсу в xml формате и загружать его содержимое (товары, которые заключены в структурах по типу <offer id="1779352490"...) в PostgreSQL таблицу со структурой, описанной ниже
2. Развернуть docker-compose [elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
3. Загрузить все товары в elasticsearch, а затем пройтись про товарам из бд; через elasticsearch найти самые похожие на обрабатываемый товар (матчи) (до 5 шт.); и загрузить их  uuid в поле similar_sku.

sql
create table public.sku
(
    uuid                   uuid,
    marketplace_id         integer,
    product_id             bigint,
    title                  text,
    description            text,
    brand                  text,
    seller_id              integer,
    seller_name            text,
    first_image_url        text,
    category_id            integer,
    category_lvl_1         text,
    category_lvl_2         text,
    category_lvl_3         text,
    category_remaining     text,
    features               json,
    rating_count           integer,
    rating_value           double precision,
    price_before_discounts real,
    discount               double precision,
    price_after_discounts  real,
    bonuses                integer,
    sales                  integer,
    inserted_at            timestamp default now(),
    updated_at             timestamp default now(),
    currency               text,
    barcode                bigint,
    similar_sku            uuid[]
);

comment on column public.sku.uuid is 'id товара в нашей бд';

comment on column public.sku.marketplace_id is 'id маркетплейса';

comment on column public.sku.product_id is 'id товара в маркетплейсе';

comment on column public.sku.title is 'название товара';

comment on column public.sku.description is 'описание товара';

comment on column public.sku.category_lvl_1 is 'Первая часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Детям".';

comment on column public.sku.category_lvl_2 is 'Вторая часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Электроника".';

comment on column public.sku.category_lvl_3 is 'Третья часть категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Детская электроника".';

comment on column public.sku.category_remaining is 'Остаток категории товара. Например, для товара, находящегося по пути Детям/Электроника/Детская электроника/Игровая консоль/Игровые консоли и игры/Игровые консоли, в это поле запишется "Игровая консоль/Игровые консоли и игры/Игровые консоли".';

comment on column public.sku.features is 'Характеристики товара';

comment on column public.sku.rating_count is 'Кол-во отзывов о товаре';

comment on column public.sku.rating_value is 'Рейтинг товара (0-5)';

comment on column public.sku.barcode is 'Штрихкод';

create index sku_brand_index
    on public.sku (brand);

create unique index sku_marketplace_id_sku_id_uindex
    on public.sku (marketplace_id, product_id);

create unique index sku_uuid_uindex
    on public.sku (uuid);



### Проблема:

Файл большой (5+гб), скорее всего полностью в оперативку не влезет, поэтому читать его нужно не полностью сразу, а по кускам (lxml.etree.iterparse в помощь)

### Требования:

- К проекту должен прикладываться файл docker-compose.yml, и сервис должен работать в docker контейнере; elasticsearch должен быть описан в этом-же композ файле (ну и, соответственно, запускаться рядом)
- Максимально-возможное кол-во полей, которые есть в файле, должны быть использованы при заполнении таблицы
- Сервис читает файл итеративно, а не весь сразу
- Код следует PEP-8 (везде есть аннотации типов и пр.)

### Дополнительные баллы за:

- Заполнение полей category_lvl_1, category_lvl_2, category_lvl_3, category_remaining данными из файла на основе categoryId из оффера и джоина на таблицу категорий в начале файла (подробнее про category_lvl_1 и пр. в коментах к полям таблицы в sql выше)
- Запуск postgres из того-же docker-compose файла, что и сервис и авто-создание таблицы при запуске проекта
- файл .pre-commit-config.yaml с линтерами и форматтерами (например - black, flake8, isort). Ну и, соответственно, использование их

### Задачи:

- Развернуть у себя docker postgres и создать там таблицу из приложенного SQL скрипта выше
- Написать сервис и провести “матчинг” через elasticsearch
- Залить сервис в github/gitlab и прислать ссылку на проект
- В readme.md файлик добавить 5-10 примеров uuid и similar_sku, которые получились после матчинга (в идеале - сделать join их с самими товарами, чтобы было понятно, что на что заматчилось)