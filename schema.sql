CREATE TABLE activities (
	pk_id SERIAL PRIMARY KEY,
	datetime DATETIME NOT NULL,
	person TEXT NOT NULL,
	service TEXT NOT NULL,
	type TEXT NOT NULL,
	content TEXT NOT NULL,
	url TEXT NOT NULL,
	UNIQUE (
		datetime,
		person(198),
		service(198),
		type (198),
		content(198),
		url(198)
	)
);
