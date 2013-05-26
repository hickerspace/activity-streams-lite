CREATE TABLE activities (
	pk_id SERIAL PRIMARY KEY,
	datetime DATETIME NOT NULL,
	person TEXT,
	service TEXT NOT NULL,
	type TEXT NOT NULL,
	content TEXT,
	url TEXT,
	UNIQUE (
		datetime,
		person(198),
		service(198),
		type (198),
		content(198),
		url(198)
	)
);
