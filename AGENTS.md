# Agent Instructions

## Audience

This file is primarily for Codex agents working in this repository. It may also
be useful for other AI coding agents such as Gemini CLI or Claude Code. It is
not intended as human-facing project documentation.

## User Context

- The repository owners are Software Engineers at the National Solar Observatory.
- The owners are responsible for High Level Software, Controls and, Data
  Management System documentation for ngGONG.
- The owners prefer thoughtful collaboration. Ask clarifying questions before
  substantial work, especially before creating structure, making broad edits, or
  committing to terminology that may affect later documentation.
- When given a task, pause briefly and consider whether the request is
  reasonable as stated or whether a better approach should be suggested.
- Clearly mark assumptions, uncertainties, and places where project decisions
  are not yet confirmed.

The assistant may jokingly refer to itself as "your new AI overlord", but should
keep technical work direct, factual, and useful.

## Project Context

- The official short name is `ngGONG`.
- The official expanded name is `Next-Generation Ground-based Solar Observing
  Network`.
- ngGONG is a continuation and upgrade of the existing GONG project, operated by
  the National Solar Observatory under NSF funding.
- The project will place telescopes at six different sites to observe the Sun
  continuously, 24 hours per day.
- Current work is aimed at a CoDR, or `Conceptual Design Review`, following NSF
  Research Infrastructure Guide (RIG) guidance for software.

## Repository Purpose

This repository is a shared working space for ngGONG High Level Software, 
Controls and Data Management System design and construction work. It will mostly
contain Markdown files that become project documentation as work proceeds toward
the Conceptual Design Review.

For now, focus on the `Software Development Plan` (`SDP`). Additional documents
may be added later, but do not create new document structures or assume the
scope of future documents without asking first.

## Documentation Guidance

- Prefer clear, durable Markdown suitable for later refinement into formal
  project documentation.
- Keep language precise and conservative. Do not invent requirements,
  commitments, architectural decisions, schedules, institutional positions, or
  funding details.
- Distinguish confirmed facts from assumptions, open questions, and proposed
  wording.
- Preserve draft status where appropriate. Avoid language that makes an
  unfinished idea sound approved.
- Use the official project naming forms: `ngGONG` and `Next-Generation
  Ground-based Solar Observing Network`.
- Define acronyms on first use in a document unless the surrounding document has
  already established them.
- Keep edits scoped to the requested documentation task. Avoid unrelated
  restructuring.
- Prefer splitting lines at the end of sentences to make file diffs more useful
  but keep in mind a soft 120 character wrap and a hard 140 character wrap.

## Working Style

- Ask questions before starting substantial documentation or repository
  structure work.
- If the requested approach seems likely to create churn, suggest a better
  approach before editing.
- Read existing files before changing them.
- Preserve user edits and do not overwrite unrelated work.
- When editing documentation, favor incremental improvements and clearly
  explain what changed.
- Do not create directories, templates, or new documents unless explicitly asked
  or the need has been confirmed.
