
CREATE TABLE public.measure (
    id serial primary key,
    latitude numeric,
    longitude numeric,
    geom public.geometry(Point,4326),
    acqtime integer,
    flightdosevd1 double precision,
    flightdosevd2 double precision,
    specvd1 integer[],
    specvd2 integer[],
    altitude double precision,
    laseralt numeric,
    radalt numeric,
    pressure numeric,
    temperature numeric,
    linenumber integer,
    filename character varying,
    mission character varying
);
