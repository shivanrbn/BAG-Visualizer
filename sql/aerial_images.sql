CREATE TABLE "data".cyclomedia_aerial_image (
	id uuid NOT NULL,
	surface_id uuid NOT NULL,
	image_width int NULL,
	image_height int NULL,
    image bytea NULL,
	CONSTRAINT aerial_pk_id PRIMARY KEY (id),
	CONSTRAINT fk_aerial_surfaces FOREIGN KEY (surface_id) REFERENCES "data".surfaces(id)
);
