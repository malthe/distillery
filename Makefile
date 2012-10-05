all: sqlalchemy django

django:
	- `which django-admin.py` test app --settings=tests.dj.settings --pythonpath=.

sqlalchemy:
	- python tests/sqla.py
