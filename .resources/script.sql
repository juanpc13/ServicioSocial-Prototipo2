-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.1
-- PostgreSQL version: 9.6
-- Project Site: pgmodeler.io
-- Model Author: ---


-- Database creation must be done outside a multicommand file.
-- These commands were put in this file only as a convenience.
-- -- object: new_database | type: DATABASE --
-- -- DROP DATABASE IF EXISTS new_database;
-- CREATE DATABASE new_database;
-- -- ddl-end --
-- 

-- object: public.acelerometro | type: TABLE --
-- DROP TABLE IF EXISTS public.acelerometro CASCADE;
CREATE TABLE public.acelerometro(
	id_acelerometro serial NOT NULL,
	id_dispositivo integer,
	x double precision,
	y double precision,
	z double precision,
	date_time timestamptz DEFAULT Now(),
	CONSTRAINT acelerometro_pk PRIMARY KEY (id_acelerometro)

);
-- ddl-end --

-- object: public.dispositivo | type: TABLE --
-- DROP TABLE IF EXISTS public.dispositivo CASCADE;
CREATE TABLE public.dispositivo(
	id_dispositivo serial NOT NULL,
	nombre character varying(64),
	mac text,
	activo boolean,
	date_time timestamptz DEFAULT Now(),
	CONSTRAINT dispositivo_pk PRIMARY KEY (id_dispositivo)

);
-- ddl-end --

-- object: public.co2 | type: TABLE --
-- DROP TABLE IF EXISTS public.co2 CASCADE;
CREATE TABLE public.co2(
	id_co2 serial NOT NULL,
	id_dispositivo integer,
	ppm double precision,
	date_time timestamptz DEFAULT Now(),
	CONSTRAINT co2_pk PRIMARY KEY (id_co2)

);
-- ddl-end --

-- object: public.h2o | type: TABLE --
-- DROP TABLE IF EXISTS public.h2o CASCADE;
CREATE TABLE public.h2o(
	id_h2o serial NOT NULL,
	id_dispositivo integer,
	rh double precision,
	date_time timestamptz DEFAULT Now(),
	CONSTRAINT co2_pk PRIMARY KEY (id_h2o)

);
-- ddl-end --

-- object: dipositivo_acelerometro_fk | type: CONSTRAINT --
-- ALTER TABLE public.acelerometro DROP CONSTRAINT IF EXISTS dipositivo_acelerometro_fk CASCADE;
ALTER TABLE public.acelerometro ADD CONSTRAINT dipositivo_acelerometro_fk FOREIGN KEY (id_dispositivo)
REFERENCES public.dispositivo (id_dispositivo) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: dispositivo_co2_fk | type: CONSTRAINT --
-- ALTER TABLE public.co2 DROP CONSTRAINT IF EXISTS dispositivo_co2_fk CASCADE;
ALTER TABLE public.co2 ADD CONSTRAINT dispositivo_co2_fk FOREIGN KEY (id_dispositivo)
REFERENCES public.dispositivo (id_dispositivo) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: dispositivo_h2o_fk | type: CONSTRAINT --
-- ALTER TABLE public.h2o DROP CONSTRAINT IF EXISTS dispositivo_h2o_fk CASCADE;
ALTER TABLE public.h2o ADD CONSTRAINT dispositivo_h2o_fk FOREIGN KEY (id_dispositivo)
REFERENCES public.dispositivo (id_dispositivo) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


