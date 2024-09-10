up:
	@docker-compose up

dup:
	@docker-compose up -d

build:
	@docker-compose build --build-arg BUILD=DEV

build_no_cache:
	@docker-compose build --no-cache --build-arg BUILD=DEV

stop:
	@docker-compose stop

down:
	@docker-compose down --remove-orphans

makemigrations:
	@docker-compose run --rm web ./manage.py makemigrations

migrate:
	@docker-compose run --rm web ./manage.py migrate

shell:
	@docker-compose run --rm web ./manage.py shell

createsuperuser:
	@docker-compose run --rm web ./manage.py createsuperuser

logs:
	@docker-compose logs -tf web

ssh_web:
	@docker exec -it time_tracker-web-1 /bin/bash

update-packages:
	@docker-compose run --rm web bash scripts/update_packages.sh

reset: down build dup
