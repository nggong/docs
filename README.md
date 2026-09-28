# ngGONG  Documentation

Docs-as-code repository for ngGONG High Level Software, Controls and Data Management System documentation.

This repository is set up as a Quarto project that can produce:

- [A GitHub Pages website](https://nggong.github.io/docs).
- A PDF book artifact.

## Local Preview

Run the local preview server through Docker:

```sh
make preview
```

Then open http://localhost:4848/.

## Local Dependencies

Local builds use Docker, so a native Quarto or LaTeX installation is not required.
Install Docker and Make using the package manager for your platform.

The Makefile builds a small local image from the same Quarto base image used by the GitHub Actions workflow.

## Build

Render the website and PDF:

```sh
make all
```

Render the website:

```sh
make html
```

Render the PDF:

```sh
make pdf
```

The website output is written to `_site/`.
The PDF output is written to `_pdf/`.

Builds generate document version metadata from Git.
A clean build from a tag such as `v0.1.0` is marked as `Release v0.1.0`; other builds are marked as drafts
using `git describe --tags --dirty --always`.

Check spelling with Vale in Docker:

```sh
make check-spelling
```

The check uses the Markdown and Quarto files tracked by Git. A local Vale
installation is not required.

Remove generated documents:

```sh
make clean
```

Remove generated documents and the local container-side Quarto cache:

```sh
make distclean
```

## Repository Layout

- `_quarto.yml` - Quarto project configuration.
- `Dockerfile` - Local/CI Quarto build image.
- `Makefile` - Convenience targets for rendering and cleaning outputs.
- `index.md` - Documentation landing page.
- `docs/` - Source documentation pages.
- `.github/workflows/` - GitHub Actions workflows for spelling checks, Pages, and PDF artifacts.

## GitHub Pages Setup

After pushing this repository to GitHub:

1. Open repository settings.
2. Go to **Pages**.
3. Set the source to **GitHub Actions**.
4. Push to `main` or run the workflow manually.
