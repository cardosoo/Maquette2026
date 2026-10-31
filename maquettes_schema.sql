--
-- PostgreSQL database dump
--

-- Dumped from database version 14.23 (Ubuntu 14.23-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.5

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: composante; Type: TABLE; Schema: public; Owner: olivier
--

CREATE TABLE public.composante (
    id integer NOT NULL,
    nom character varying(255) NOT NULL,
    code character varying(128) NOT NULL
);


ALTER TABLE public.composante OWNER TO olivier;

--
-- Name: composante_id_seq; Type: SEQUENCE; Schema: public; Owner: olivier
--

CREATE SEQUENCE public.composante_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.composante_id_seq OWNER TO olivier;

--
-- Name: composante_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivier
--

ALTER SEQUENCE public.composante_id_seq OWNED BY public.composante.id;


--
-- Name: ecue; Type: TABLE; Schema: public; Owner: olivier
--

CREATE TABLE public.ecue (
    id integer NOT NULL,
    nom character varying(128) NOT NULL,
    code character varying(128) NOT NULL,
    periode character varying(128) NOT NULL,
    etape_id integer NOT NULL,
    effectif integer NOT NULL,
    besoins json NOT NULL
);


ALTER TABLE public.ecue OWNER TO olivier;

--
-- Name: ecue_etape; Type: TABLE; Schema: public; Owner: olivier
--

CREATE TABLE public.ecue_etape (
    id integer NOT NULL,
    ecue_id integer NOT NULL,
    etape_id integer NOT NULL,
    effectif integer NOT NULL
);


ALTER TABLE public.ecue_etape OWNER TO olivier;

--
-- Name: ecue_etape_id_seq; Type: SEQUENCE; Schema: public; Owner: olivier
--

CREATE SEQUENCE public.ecue_etape_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ecue_etape_id_seq OWNER TO olivier;

--
-- Name: ecue_etape_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivier
--

ALTER SEQUENCE public.ecue_etape_id_seq OWNED BY public.ecue_etape.id;


--
-- Name: ecue_id_seq; Type: SEQUENCE; Schema: public; Owner: olivier
--

CREATE SEQUENCE public.ecue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ecue_id_seq OWNER TO olivier;

--
-- Name: ecue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivier
--

ALTER SEQUENCE public.ecue_id_seq OWNED BY public.ecue.id;


--
-- Name: etape; Type: TABLE; Schema: public; Owner: olivier
--

CREATE TABLE public.etape (
    id integer NOT NULL,
    nom character varying(128) NOT NULL,
    code character varying(128) NOT NULL,
    type character varying(128) NOT NULL,
    niveau character varying(128) NOT NULL,
    domaine character varying(128) NOT NULL,
    effectif integer NOT NULL,
    composante_id integer NOT NULL
);


ALTER TABLE public.etape OWNER TO olivier;

--
-- Name: etape_id_seq; Type: SEQUENCE; Schema: public; Owner: olivier
--

CREATE SEQUENCE public.etape_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.etape_id_seq OWNER TO olivier;

--
-- Name: etape_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivier
--

ALTER SEQUENCE public.etape_id_seq OWNED BY public.etape.id;


--
-- Name: composante id; Type: DEFAULT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.composante ALTER COLUMN id SET DEFAULT nextval('public.composante_id_seq'::regclass);


--
-- Name: ecue id; Type: DEFAULT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue ALTER COLUMN id SET DEFAULT nextval('public.ecue_id_seq'::regclass);


--
-- Name: ecue_etape id; Type: DEFAULT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue_etape ALTER COLUMN id SET DEFAULT nextval('public.ecue_etape_id_seq'::regclass);


--
-- Name: etape id; Type: DEFAULT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.etape ALTER COLUMN id SET DEFAULT nextval('public.etape_id_seq'::regclass);


--
-- Name: composante composante_code_key; Type: CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.composante
    ADD CONSTRAINT composante_code_key UNIQUE (code);


--
-- Name: composante composante_pkey; Type: CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.composante
    ADD CONSTRAINT composante_pkey PRIMARY KEY (id);


--
-- Name: ecue_etape ecue_etape_pkey; Type: CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue_etape
    ADD CONSTRAINT ecue_etape_pkey PRIMARY KEY (id);


--
-- Name: ecue ecue_pkey; Type: CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue
    ADD CONSTRAINT ecue_pkey PRIMARY KEY (id);


--
-- Name: etape etape_pkey; Type: CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.etape
    ADD CONSTRAINT etape_pkey PRIMARY KEY (id);


--
-- Name: ecue_i_4db226; Type: INDEX; Schema: public; Owner: olivier
--

CREATE INDEX ecue_i_4db226 ON public.ecue USING btree (code);


--
-- Name: etape_i_4db226; Type: INDEX; Schema: public; Owner: olivier
--

CREATE INDEX etape_i_4db226 ON public.etape USING btree (code);


--
-- Name: ix_composante_code; Type: INDEX; Schema: public; Owner: olivier
--

CREATE INDEX ix_composante_code ON public.composante USING btree (code);


--
-- Name: ecue_etape ecue_etape_ecue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue_etape
    ADD CONSTRAINT ecue_etape_ecue_id_fkey FOREIGN KEY (ecue_id) REFERENCES public.ecue(id) ON DELETE CASCADE;


--
-- Name: ecue_etape ecue_etape_etape_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue_etape
    ADD CONSTRAINT ecue_etape_etape_id_fkey FOREIGN KEY (etape_id) REFERENCES public.etape(id) ON DELETE CASCADE;


--
-- Name: ecue ecue_etape_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.ecue
    ADD CONSTRAINT ecue_etape_id_fkey FOREIGN KEY (etape_id) REFERENCES public.etape(id) ON DELETE CASCADE;


--
-- Name: etape etape_composante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivier
--

ALTER TABLE ONLY public.etape
    ADD CONSTRAINT etape_composante_id_fkey FOREIGN KEY (composante_id) REFERENCES public.composante(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

