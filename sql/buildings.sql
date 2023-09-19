CREATE TABLE "data".buildings AS 
SELECT 
split_part(pand.identificatie,'.', 4) AS id 
, geometrie AS geometry 
FROM bag3d.pand;

-- add primary key
ALTER TABLE data.buildings 
ADD PRIMARY KEY (id); 
