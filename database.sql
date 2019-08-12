-- we don't know how to generate root <with-no-name> (class Root) :(
create table CASE_NUMBER
(
	ID INT not null
		constraint CASE_NUMBER_PK
			primary key
		unique,
	COURT_NAME TEXT not null,
	CASE_NUMBER INT not null
);

create unique index CASE_NUMBER_COURT_uindex
	on CASE_NUMBER (COURT_NAME);

create table CREDITOR
(
	CREDITOR TEXT not null
		constraint CREDITOR_pk
			primary key
);

create table MATCHED_CASE
(
	COURT_NAME TEXT not null
		constraint MATCHED_CASE_CASE_NUMBER_COURT_NAME_fk
			references CASE_NUMBER (COURT_NAME),
	CASE_NUMBER INTEGER not null
		constraint MATCHED_CASE_pk
			primary key,
	YEAR INTEGER,
	JUDGE TEXT,
	DATE_FILED TEXT,
	TIME_FILED TEXT,
	PLAINTIFF_NAME TEXT,
	DEFENDANT_NAME TEXT,
	DEFENDANT_HOUSE TEXT,
	DEFENDANT_STREET TEXT,
	DEFENDANT_APT TEXT,
	DEFENDANT_CITY TEXT,
	DEFENDANT_STATE TEXT,
	DEFENDANT_ZIP INTEGER,
	DEFENDANT_EMAIL TEXT,
	DEFENDANT_FACEBOOK TEXT
);

create table NEW_CASE
(
	COURT_NAME     TEXT    not null
		constraint NEW_CASE_CASE_NUMBER_COURT_NAME_fk
			references CASE_NUMBER (COURT_NAME),
	CASE_NUMBER    INTEGER not null
		constraint NEW_CASE_pk
			primary key,
	YEAR           INTEGER,
	JUDGE          TEXT,
	DATE_FILED     TEXT,
	TIME_FILED     TEXT,
	PLAINTIFF_NAME TEXT,
	DEFENDANT_NAME TEXT
);

create table POSSIBLE_CASE
(
	COURT_NAME TEXT not null
		constraint POSSIBLE_CASE_CASE_NUMBER_COURT_NAME_fk
			references CASE_NUMBER (COURT_NAME),
	CASE_NUMBER INTEGER not null
		constraint POSSIBLE_CASE_pk
			primary key,
	YEAR INTEGER,
	JUDGE TEXT,
	DATE_FILED TEXT,
	TIME_FILED TEXT,
	PLAINTIFF_NAME TEXT,
	DEFENDANT_NAME TEXT
);

create table PROCESSED_CASE
(
	COURT_NAME TEXT not null
		constraint PROCESSED_CASE_CASE_NUMBER_COURT_NAME_fk
			references CASE_NUMBER (COURT_NAME),
	CASE_NUMBER INTEGER not null
		constraint PROCESSED_CASE_pk
			primary key,
	YEAR INTEGER,
	JUDGE TEXT,
	DATE_FILED TEXT,
	TIME_FILED TEXT,
	PLAINTIFF_NAME TEXT,
	DEFENDANT_NAME TEXT,
	DEFENDANT_HOUSE TEXT,
	DEFENDANT_STREET TEXT,
	DEFENDANT_APT TEXT,
	DEFENDANT_CITY TEXT,
	DEFENDANT_STATE TEXT,
	DEFENDANT_ZIP INTEGER,
	DEFENDANT_EMAIL TEXT,
	DEFENDANT_FACEBOOK TEXT,
	MAIL_TIMESTAMP TEXT,
	EMAIL_TIMESTAMP TEXT,
	FB_TIMESTAMP TEXT
);

create table REJECTED_CASE
(
	COURT_NAME TEXT not null
		constraint REJECTED_CASE_CASE_NUMBER_COURT_NAME_fk
			references CASE_NUMBER (COURT_NAME),
	CASE_NUMBER INTEGER not null
		constraint REJECTED_CASE_pk
			primary key,
	YEAR INTEGER,
	JUDGE TEXT,
	DATE_FILED TEXT,
	TIME_FILED TEXT,
	PLAINTIFF_NAME TEXT,
	DEFENDANT_NAME TEXT,
	REJECTED_REASON TEXT
);

