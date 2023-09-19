/*TODO create autoincrement serial or uuid for this! */
CREATE TABLE bag3d.surfaces_lod22_3d (
	id uuid
	, bag_building_id varchar(20)
	, semantics_value integer 
	, surface_type varchar 
	, surface_geometry geometry

)


create table bag3d.surfaces_lod22_3d as
with unnested_surfaces as (
SELECT gid
, fid
, unnest(semantics_values) as semantics_value
, (ST_DUMP(geometrie)).geom  AS geom 
, geometrie 
FROM bag3d.lod22_3d)
select gid
, split_part(pand.identificatie,'.', 4) as bag_building_id
, semantics_value 
, case when semantics_value::int = 0 then 'GroundSurface'
	when semantics_value::int = 1 then 'RoofSurface'
	when semantics_value::int = 2 then 'OuterWallSurface'
	when semantics_value::int = 3 then 'InnerWallSurface'
end as surface_type
, st_transform(geom, 28992) as surface_geometry -- transform to EPSG 28992 coordinates, dutch coordinates, instead of WSG84
from unnested_surfaces
join bag3d.pand on 
unnested_surfaces.fid = pand.fid;

CREATE INDEX surfaces_3d_bag_building_ids ON bag3d.surfaces_lod22_3d  (bag_building_id);