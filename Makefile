DGRAPH_VERSION = latest

up: ## Start the zero and alpha containers
	DGRAPH_VERSION=$(DGRAPH_VERSION) docker-compose up

down: ## Stop the containers
	DGRAPH_VERSION=$(DGRAPH_VERSION) docker-compose stop

schema: ## Set the schema
	curl --data-binary '@schema.graphql' http://localhost:8080/admin/schema

drop-data: ## Drops all data (but not the schema)
	curl -X POST localhost:8080/alter -d '{"drop_op": "DATA"}'

drop-all: ## Drops data and schema
	curl -X POST localhost:8080/alter -d '{"drop_all": true}'

import: ## Import data
	python episode_importer.py
	python script_importer.py

build-image: ## Build the self-contained Dgraph and Jupyter Lab image
	# need to be logged in to dockerhub for this to work, `docker login -u matthewmcneely`
	docker buildx build --platform linux/amd64 --platform linux/arm64 -t matthewmcneely/dgraph-vector-experiment --output=type=registry .

run-image: ## Run the self-contained Dgraph and Jupyter Lab image
	docker run -p 8080:8080 -p 9080:9080 matthewmcneely/dgraph-vector-experiment

help: ## Print target help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

