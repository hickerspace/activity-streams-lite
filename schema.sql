CREATE TABLE activities (
  pk_id SERIAL,
	datetime DATETIME NOT NULL,
	person TEXT,
	service TEXT NOT NULL,
	type TEXT NOT NULL,
	content TEXT,
	url TEXT,
	PRIMARY KEY (pk_id),
	UNIQUE (
		datetime,
		person(198),
		service(198),
		TYPE (198),
		content(198),
		url(198)
	)
);
