KIND = $(shell which kind)
KUBECTL = $(shell which kubectl)


cluster:
	$(KIND) create $(@) --name=sample --config=kind.yaml

# more coming soon.