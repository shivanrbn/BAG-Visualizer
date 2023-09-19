CREATE TABLE "data".cyclomedia_streetview_images (
	id uuid NOT NULL,
	panorama_id varchar NULL,
	surface_id uuid not null,
	image_width int NULL,
	image_height int4 NULL,
	image bytea NULL,
	CONSTRAINT pk_image_id PRIMARY KEY (id),
	CONSTRAINT fk_streeview_surface FOREIGN KEY (surface_id) REFERENCES "data".surfaces(id),
	CONSTRAINT unique_pano_surface_uk UNIQUE (panorama_id, surface_id)
);
