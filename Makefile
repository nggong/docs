QUARTO_IMAGE ?= ghcr.io/quarto-dev/quarto:1.9.38
DOCS_IMAGE ?= nggong-docs-quarto:local
QUARTO_HOME := .quarto-home
PDF_STAGING := .quarto-pdf

DOCKER_RUN = docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--env HOME=/project/$(QUARTO_HOME) \
	--volume "$(CURDIR):/project" \
	--workdir /project \
	$(DOCS_IMAGE)

.PHONY: all image html pdf preview clean distclean

all: image $(QUARTO_HOME)/.tinytex-ready
	$(DOCKER_RUN) quarto render --to pdf
	rm -rf $(PDF_STAGING)
	mkdir -p $(PDF_STAGING)
	cp _site/*.pdf $(PDF_STAGING)/
	$(DOCKER_RUN) quarto render --to html
	cp $(PDF_STAGING)/*.pdf _site/

image:
	docker build --build-arg QUARTO_IMAGE=$(QUARTO_IMAGE) --tag $(DOCS_IMAGE) .

html: image
	$(DOCKER_RUN) quarto render --to html

pdf: $(QUARTO_HOME)/.tinytex-ready
	$(DOCKER_RUN) quarto render --to pdf

$(QUARTO_HOME)/.tinytex-ready: image
	mkdir -p $(QUARTO_HOME)
	$(DOCKER_RUN) quarto install tinytex --no-prompt
	touch $(QUARTO_HOME)/.tinytex-ready

preview: image
	docker run --rm -it \
		--user "$$(id -u):$$(id -g)" \
		--env HOME=/project/$(QUARTO_HOME) \
		--publish 4848:4848 \
		--volume "$(CURDIR):/project" \
		--workdir /project \
		$(DOCS_IMAGE) quarto preview --host 0.0.0.0 --port 4848

clean:
	rm -rf _site .quarto _freeze $(PDF_STAGING)

distclean: clean
	rm -rf $(QUARTO_HOME)
