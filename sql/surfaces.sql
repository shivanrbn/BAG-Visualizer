CREATE TABLE "data".surfaces (
	id uuid NOT NULL,
	bag_building_id varchar(20) NULL,
	semantics_value int4 NULL,
	surface_type varchar NULL,
	surface_geometry geometry NULL,
	CONSTRAINT pk_id PRIMARY KEY (id),
	CONSTRAINT surfaces_bag_building_id_fk FOREIGN KEY (bag_building_id) REFERENCES "data".buildings(id)
);

-- create temp table, not inserting directly because temp table generation uses parallel workers.
create temp table surfaces_split as 
with unnested_surfaces as (
SELECT uuid_generate_v4() as uuid
, fid 
, unnest(semantics_values) as semantics_value
, (ST_DUMP(geometrie)).geom  AS geom 
FROM bag3d.lod22_3d)
select uuid
, split_part(pand.identificatie,'.', 4) as bag_building_id
, semantics_value as semantics_value
, case when semantics_value::int = 0 then 'GroundSurface'
	when semantics_value::int = 1 then 'RoofSurface'
	when semantics_value::int = 2 then 'OuterWallSurface'
	when semantics_value::int = 3 then 'InnerWallSurface'
end as surface_type
, st_transform(geom, 28992) as surface_geometry -- dutch (Amersfoort) CRS. 
from unnested_surfaces
join bag3d.pand on 
unnested_surfaces.fid = pand.fid;
unnested_surfaces.fid = pand.fid;

-- insert
insert into "data".surfaces 
select * from surfaces_split;

-- index creating else querying will take VERY long.
CREATE INDEX surfaces_3d_bag_building_ids ON data.surfaces (bag_building_id);
CREATE INDEX surfaces_3d_id ON data.surfaces (id);