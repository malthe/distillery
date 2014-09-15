all: sqlalchemy django

django:
	- `which django-admin.py` test --settings=tests.dj.settings --pythonpath=.

sqlalchemy:
	- python tests/sqla.py
