# ngGONG  Documentation

Docs-as-code repository for ngGONG High Level Software, Controls and Data Management System documentation.

This repository is set up as a Quarto project that can produce:

- [A GitHub Pages website](https://nggong.github.io/docs).
- A separate PDF for the Software Development Plan.

## Local Preview

Run the local preview server through Docker:

```sh
make preview
```

Then open http://localhost:4848/.
The preview footer displays `PREVIEW` instead of a Git-derived version.

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

Render the formal-document PDFs:

```sh
make pdf
```

The website output is written to `_site/`.
PDFs are written under `_pdf/`, preserving their source paths:

- `_pdf/docs/software-development-plan.pdf`

`make html` builds the PDFs first so that the website's PDF download links work.
`make preview` does not build PDFs; its download links require a prior PDF build and may point to older files.
The website includes these files under `_site/_pdf/`.
Developer guides and SCS release guidance are published as web pages only.

The website navigation is defined in `_quarto-website.yml`, with unnumbered, nested content groups.
Its render rules publish documents under `docs/` while excluding the existing unlisted HLS design draft.
New documents under `docs/` will be published by default; add them to the navigation or explicitly exclude them while they are drafts.
The SDP remains one online page for now.

The `pdf` profile in `_quarto-pdf.yml` selects the formal documents and their shared PDF settings.
To add a formal document later, add its entry document to that profile's render list and give its website page a PDF link.
A document can assemble multiple Markdown sources with Quarto's `include` shortcode;
keep included fragments out of the website render list unless they are intended as standalone pages.
PDF selection is independent of the website sidebar.
Section numbers belong to each PDF rather than the whole website.

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

## Automated Pull Request Review

The AI review workflow uses the official Codex GitHub Action to review pull
requests according to the rules in `AGENTS.md`.
To enable it, configure an Actions repository secret named `OPENAI_API_KEY`.
If the secret is absent or unavailable to the event, the workflow succeeds and
records that the review was skipped.

## Repository Layout

- `_quarto.yml` - Shared metadata and default website profile.
- `_quarto-website.yml` - Website configuration and navigation.
- `_quarto-pdf.yml` - Formal-document PDF selection and formatting.
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
