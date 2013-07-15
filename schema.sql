CREATE TABLE activities (
	pk_id SERIAL PRIMARY KEY,
	datetime DATETIME NOT NULL,
	person TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	service TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	type TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	account TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	content TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	url TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	UNIQUE (
		datetime,
		person (30),
		service (30),
		type (30),
		content (165),
		url (75)
	)
) DEFAULT CHARSET=utf8;

CREATE TABLE last_update (
	id SERIAL PRIMARY KEY,
	datetime DATETIME NOT NULL,
	service TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	type TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	account TEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
	error tinyint(1) NOT NULL,
	UNIQUE (
		service (100),
		type (100),
		account(100)
	)
) DEFAULT CHARSET=utf8;
