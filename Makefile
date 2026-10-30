QUARTO_IMAGE ?= ghcr.io/quarto-dev/quarto:1.9.38
DOCS_IMAGE ?= nggong-docs-quarto:local
VALE_IMAGE ?= jdkato/vale:v3.17.0
QUARTO_HOME := .quarto-home
PDF_OUTPUT_DIR := _pdf
# Preview settings must apply to both renders; --profile replaces QUARTO_PROFILE.
HTML_PROFILE := website
PDF_PROFILE := pdf
ifneq ($(DOCS_PREVIEW),)
HTML_PROFILE := pr-preview,website
PDF_PROFILE := pr-preview,pdf
endif
VALE_FILES := $(shell git ls-files -- '*.md' '*.qmd' ':(exclude)AGENTS.md' ':(exclude)**/AGENTS.md')

DOCKER_RUN = docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--env HOME=/project/$(QUARTO_HOME) \
	--volume "$(CURDIR):/project" \
	--workdir /project \
	$(DOCS_IMAGE)

VALE_RUN = docker run --rm \
	--user "$$(id -u):$$(id -g)" \
	--volume "$(CURDIR):/project" \
	--workdir /project \
	$(VALE_IMAGE)

.PHONY: all check check-spelling image html pdf preview clean distclean version

all: html

check: check-spelling

check-spelling:
	$(VALE_RUN) $(VALE_FILES)

image:
	docker build --build-arg QUARTO_IMAGE=$(QUARTO_IMAGE) --tag $(DOCS_IMAGE) .

html: pdf
	$(DOCKER_RUN) quarto render --profile $(HTML_PROFILE) --to html

pdf: $(QUARTO_HOME)/.tinytex-ready version
	$(DOCKER_RUN) quarto render --profile $(PDF_PROFILE) --to pdf --output-dir $(PDF_OUTPUT_DIR)

version:
	./tools/doc-version.sh

$(QUARTO_HOME)/.tinytex-ready: image
	mkdir -p $(QUARTO_HOME)
	$(DOCKER_RUN) quarto install tinytex --no-prompt
	touch $(QUARTO_HOME)/.tinytex-ready

preview: image version
	docker run --rm -it \
		--user "$$(id -u):$$(id -g)" \
		--env HOME=/project/$(QUARTO_HOME) \
		--publish 4848:4848 \
		--volume "$(CURDIR):/project" \
		--workdir /project \
		$(DOCS_IMAGE) quarto preview --host 0.0.0.0 --port 4848 \
		--metadata doc-status: --metadata doc-version:PREVIEW

clean:
	rm -rf _site $(PDF_OUTPUT_DIR) .quarto-pdf .quarto _freeze

distclean: clean
	rm -rf $(QUARTO_HOME)
