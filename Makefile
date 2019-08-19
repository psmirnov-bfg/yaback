operation ?= "up"

run:
	docker-compose up -d --build
	@docker-compose exec main python tests/test.py

stop:
	docker-compose down

clean: | stop
	rm -rf _data

get_goose:
	@echo "Installing goose2"
	@mkdir -p _data/bin
	@docker run --rm -v $(shell pwd)/_data/bin:/go/bin golang:1.11.0 go get -u github.com/bfg-dev/goose/cmd/goose2
	@echo "Done"

migrate:
	@echo "Run migrations..."
	@docker-compose run --rm migrator goose2 -dir /migrations -force-holes postgres "postgres://postgres:postgres@postgresql/postgres?sslmode=disable" $(operation)
	@echo "migrations done"

setup: run get_goose migrate test
	@echo "ALL done"

test:
	@echo "Run tests..."
	@docker-compose exec main pytest -s -q tests/example_test.py
	@echo "tests done"