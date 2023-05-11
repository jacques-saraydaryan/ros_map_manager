#!/bin/bash
set -e
export PGPASSWORD=$POSTGRES_PASSWORD;
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE "$APP_DB_NAME" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';
  ALTER DATABASE "$APP_DB_NAME" OWNER TO "$POSTGRES_USER";
  \connect -reuse-previous=on "dbname='$APP_DB_NAME'"
  CREATE EXTENSION postgis;
  CREATE EXTENSION postgis_raster;
  COMMIT;
  DROP TABLE IF EXISTS public."object";

CREATE TABLE public."object"
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    coordinate geometry NOT NULL,
    type character varying COLLATE pg_catalog."default" NOT NULL,
    type_name character varying COLLATE pg_catalog."default",
    orient_x double precision,
    orient_y double precision,
    orient_z double precision,
    orient_w double precision,
    ttl real NOT NULL,
    confidence real,
    update_date timestamp without time zone NOT NULL DEFAULT (now() at time zone 'utc'),
    count double precision,
    json_payload character varying COLLATE pg_catalog."default",
    CONSTRAINT "object_pkey" PRIMARY KEY (id)
);


SET standard_conforming_strings = OFF;
SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';
DROP TABLE IF EXISTS public."room";
-- DELETE FROM geometry_columns WHERE f_table_name = 'room' AND f_table_schema = 'public';
-- BEGIN;


CREATE TABLE public."room" ( "ogc_fid" SERIAL, CONSTRAINT "room_pk" PRIMARY KEY ("ogc_fid") );
SELECT AddGeometryColumn('public','room','poly',4326,'POLYGON',2);
CREATE INDEX "room_Room_geom_idx" ON "public"."room" USING GIST ("poly");

ALTER TABLE public."room" ADD COLUMN "room" VARCHAR(10);
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E61000000100000007000000DA39B8118C6CFA3F3041829E8E9B0F4026FD73732A5EF63F3041829E8E9B0F404274EF7B07D4F43F357A59F8A8BFF03F1089A7434DDA1440E00327D69350EE3F7C1EACD36105154084C89C4F2E080F407C1EACD36105154084C89C4F2E080F40DA39B8118C6CFA3F3041829E8E9B0F40', 'Kitchen');
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E61000000100000006000000C513C88546F1F43F289A860DBCBAED3FBDB52EA28102F43FC8C60D098D4BF3BF7094D44C02A01440D024A7EC513AF4BF02219E5E3DD414401C8D20B89454EC3F02219E5E3DD414401C8D20B89454EC3FC513C88546F1F43F289A860DBCBAED3F', 'Bedroom');
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E61000000100000006000000920BB64F3A15FBBF9CB15F37E7321040181269FA4DC8FBBF661416BFE6141D4048B4315FB0061640C1A39C62BF701C40C2AD7EB49C531540AEAD3F52583B0F40C2AD7EB49C531540AEAD3F52583B0F40920BB64F3A15FBBF9CB15F37E7321040', 'LivingRoom');
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E6100000010000000C000000E49E6885D7D7F33FE4D5AF951C4BF4BF143883B27491F13F9D1C0A28B0B213C0F414DBEC67B1F93FE7E512E1AE8214C06A1676AD115F02406D602D8D7B9714C06A1676AD115F0240259724D47CC713C031AFBA531741104041818E84AF1A14C0A934A0A74A2C104029746266E56512C02518019DDD651440BDE3B16A4BA412C0CB7C85F9DCCD1440AC035753A504FFBF9B3F6B4FB10210406C2F83F23F5EFEBF9B3F6B4FB102104020AA83F681F1F4BFE49E6885D7D7F33FE4D5AF951C4BF4BF', 'Bedroom2');
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E610000001000000050000005C7810890E3BFDBFF37B78A5170D1040DCB80367B79000C0F9B785CBB04A13C03422ED62A7E4F13F259724D47CC713C0941BE4A707CBF53FD702BCF295F00F405C7810890E3BFDBFF37B78A5170D1040', 'Corridor');
-- INSERT INTO public."room" ("poly" , "room") VALUES ('0103000020E610000001000000060000002DFFF6D3E5D100C0A42E60FCD47413C0177FADC8030601C03A5CBF01982119C02C2976E342DFF73F108C952C508319C0F4683EC78D61F83F6A3EBF9EA3FD13C0A4EB2425ED11F23F83EE71EB01C313C02DFFF6D3E5D100C0A42E60FCD47413C0', 'Cupboard');
INSERT INTO public.room (ogc_fid, poly, room) VALUES (7, '0103000020E61000000100000005000000AC2697854829E3BF6A7632FA3BCE14404E5790B8F8EE0A401B24010931831440F244413FD4F409404646D3EDCA6600402070D36ADA11E7BFE227719949820140AC2697854829E3BF6A7632FA3BCE1440', 'Room_2');
INSERT INTO public.room (ogc_fid, poly, room) VALUES (8, '0103000020E610000001000000050000009C0E71CF8E54E7BF42C049809C710140F244413FD4F409404646D3EDCA660040F244413FD4F40940B806958FEAB7ECBF1095E87D89C2EBBF4037CF3C2ADAE9BF9C0E71CF8E54E7BF42C049809C710140', 'Room_1');


DROP TABLE IF EXISTS public."map_raster";
CREATE TABLE map_raster(rid serial primary key, map raster);

--TABLESPACE pg_default;

ALTER TABLE public."object"
    OWNER to postgres;

ALTER TABLE public."room"
    OWNER to postgres;

ALTER TABLE public."map_raster"
    OWNER to postgres;

COMMIT;
EOSQL

