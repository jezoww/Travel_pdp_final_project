mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

admin:
	python3 manage.py createsuperuser


udb:
	rm -rf db.sqlite3
	rm -rf user/migrations/*
	rm -rf travel/migrations/*
	touch user/migrations/__init__.py
	touch travel/migrations/__init__.py
	python3 manage.py makemigrations
	python3 manage.py migrate

celery:
	celery -A root worker --loglevel=info

