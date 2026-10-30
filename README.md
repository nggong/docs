# ngGONG  Documentation

Docs-as-code repository for ngGONG High Level Software, Controls and Data Management System documentation.

This repository is set up as a Quarto project that can produce:

- [A GitHub Pages website](https://nggong.github.io/docs).
- Separate PDFs for the Software Development Plan and the Software Conceptual Design.

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
- `_pdf/docs/design/software-conceptual-design.pdf`

`make html` builds the PDFs first so that the website's PDF download links work.
`make preview` does not build PDFs; its download links require a prior PDF build and may point to older files.
The website includes these files under `_site/_pdf/`.
Developer guides and SCS release guidance are published as web pages only.

The website navigation is defined in `_quarto-website.yml`, with unnumbered, nested content groups.
Its render rules publish documents under `docs/`.
New documents under `docs/` will be published by default; add them to the navigation or explicitly exclude them while they are drafts.
The SDP remains one online page for now.

The `pdf` profile in `_quarto-pdf.yml` selects the formal documents and their shared PDF settings.
To add a formal document later, add its entry document to that profile's render list and give its website page a PDF link.
A document can assemble multiple Markdown sources with Quarto's `include` shortcode;
keep included fragments out of the website render list unless they are intended as standalone pages.
The Software Conceptual Design is assembled by `docs/design/software-conceptual-design.qmd` from the section files in
`docs/design/_conceptual/`. The include order in the entry document sets the section order in both outputs.
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

## Pull Request Previews

Pull requests targeting `main`, including drafts, build HTML and all configured PDFs.
For branches in this repository, successful builds are published at:

```text
https://nggong.github.io/docs/pr/<PR-number>/
```

The existing PDF download links point to that preview's PDFs.
The preview banner shows the PR number and source commit.
Builds render the PR head commit rather than GitHub's temporary merge commit.
Fork PRs build downloadable artifacts but are not published automatically.
All published previews are public.

`Build Documentation` uploads the complete website and a separate PDF artifact.
`Publish Documentation` runs trusted code from `main`, updates generated output on the `gh-pages` storage branch,
and deploys the combined production site and previews using GitHub Actions.
Keep the Pages source set to **GitHub Actions**; do not select the storage branch as the publishing source.
Production updates preserve previews, and PR updates replace only that PR's directory.
Closing or merging a PR removes its preview; each publisher run also removes previews for other closed PRs.
Reopening a PR starts a new build and restores the preview.
Publish updates queue rather than cancel one another.
Old builds are skipped when their source commit no longer matches the PR or production ref.
The publisher records build run IDs to prevent older builds from replacing newer output.
Tag builds (`v*`) retain the existing behavior of updating the production site.
The most recent accepted production build run takes precedence across main and tag builds.

The publisher's Actions job summary links to the published content after assembly;
confirm that its deployment step succeeded before using the link.
A failed build leaves the last successful preview in place; compare its banner commit with the PR head.
A failed deployment can be retried by rerunning the publisher workflow.
To publish a specific successful build, manually run **Publish Documentation** from `main`
and supply its **Build Documentation run ID** (the number in the build's Actions URL).
Leave the input blank to reconcile cleanup and redeploy stored content.
Build artifacts must still be available for a retry that supplies a run ID.

### Initial Setup

GitHub requires the `workflow_run` publisher to exist on the default branch before it can run.
The first PR introducing these workflows can verify builds and downloadable artifacts;
its hosted preview cannot run automatically until the publisher is merged into `main`.
After that merge, the main build seeds the production output and subsequent PRs can publish previews.
An already open PR can publish by pushing another commit or manually publishing its successful build run ID.
If a preview is stored before the first production build, deployment waits for a production home page.

The publishing job needs `contents: write`, `actions: read`, `pull-requests: read`,
`pages: write`, and `id-token: write` permissions.
Repository or organization policy must permit these permissions and creation of the `gh-pages` branch.
The existing `github-pages` environment must allow publishing workflows on `main`.
Any environment approval rules still apply.
Do not edit generated files on `gh-pages` by hand.
Previews share the GitHub Pages site size limit with production, so closed previews are removed rather than archived.

Run local publishing tests without GitHub access:

```sh
python3 tools/test_publish_site.py
```

## Repository Layout

- `_quarto.yml` - Shared metadata and default website profile.
- `_quarto-website.yml` - Website configuration and navigation.
- `_quarto-pdf.yml` - Formal-document PDF selection and formatting.
- `Dockerfile` - Local/CI Quarto build image.
- `Makefile` - Convenience targets for rendering and cleaning outputs.
- `index.md` - Documentation landing page.
- `docs/` - Source documentation pages.
- `.github/workflows/` - GitHub Actions workflows for spelling checks, builds, and Pages publishing.

## GitHub Pages Setup

After pushing this repository to GitHub:

1. Open repository settings.
2. Go to **Pages**.
3. Set the source to **GitHub Actions**.
4. Push to `main` or run the workflow manually.
