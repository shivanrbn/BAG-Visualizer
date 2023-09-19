CREATE TABLE "data".images (
	image_id uuid NOT NULL,
	panoram_id varchar NOT NULL,
	surface_id uuid NOT NULL,
	image_width int NULL,
	image_height int NULL,
    image bytea NULL,
	CONSTRAINT image_pk_id PRIMARY KEY (id)
);
