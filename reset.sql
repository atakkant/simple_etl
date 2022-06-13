drop table products;
drop table asin_list;
drop table brand;
drop table salesrank;
drop table upper_category;
drop table mid_category;
drop table min_category;
drop table raw_products;

create table asin_list (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    asin VARCHAR(50) NOT NULL
);

create table brand (
    id SERIAL NOT NULL PRIMARY KEY,
    brand_name VARCHAR(250) NOT NULL
);

create table upper_category (
    id SERIAL NOT NULL PRIMARY KEY,
    up_cat_name VARCHAR(50) NOT NULL
);

create table mid_category (
    id SERIAL NOT NULL PRIMARY KEY,
    mid_cat_name VARCHAR(50) NOT NULL
);

create table min_category (
    id SERIAL NOT NULL PRIMARY KEY,
    min_cat_name VARCHAR(50) NOT NULL
);

create table salesrank (
    id SERIAL NOT NULL PRIMARY KEY,
    salesrank_cat_name VARCHAR(50) NOT NULL
);

create table products (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    asin_id BIGINT NOT NULL REFERENCES asin_list (id),
    price REAL,
    title VARCHAR(250),
    description TEXT,
    up_cat INT REFERENCES upper_category (id),
    mid_cat INT REFERENCES mid_category (id),
    min_cat INT REFERENCES min_category (id),
    imurl VARCHAR(3000),
    also_bought TEXT,
    also_viewed TEXT,
    bought_together TEXT,
    salesrank_cat_id INT REFERENCES salesrank (id),
    salesrank_value INT,
    brand_id INT REFERENCES brand (id),
    UNIQUE(asin_id)
);

create table raw_products (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    asin VARCHAR(50) NOT NULL,
    title TEXT,
    description TEXT,
    price REAL,
    categories TEXT [][],
    imurl TEXT,
    related JSON,
    salesrank JSON,
    brand TEXT
);