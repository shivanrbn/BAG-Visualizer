CREATE TABLE "data".cyclomedia_streetview_panorama (
	id varchar NOT NULL,
	panorama_id varchar NOT NULL,
	surface_id UUID not null,
	recording_location geometry NULL,
	recording_date date NULL,
	CONSTRAINT panorama_pk_od PRIMARY KEY (id),
	CONSTRAINT fk_streetview_image FOREIGN KEY (panorama_id,surface_id) REFERENCES "data".cyclomedia_streetview_images(panorama_id, surface_id)
);
