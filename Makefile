all: db_reset debug

debug:
	. venv/bin/activate && \
	python3 src/main.py

run: db_reset
	. venv/bin/activate && \
	cd src && \
	gunicorn -w 3 main:app -b 0.0.0.0:80

docker:
	docker compose up

venv:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt

_deps_linux:
	sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev \
		 build-essential

clean:
	find src -type d -name __pycache__ | xargs rm -rf

db_reset:
	. venv/bin/activate && \
	python3 src/db_init.py

db_dummy:
	. venv/bin/activate && \
	python3 src/db_create_fake_data.py

