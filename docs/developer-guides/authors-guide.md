<!--
Purpose: Explain how to keep documentation consistent with its purpose, audience, and writing style.
Audience: This guide is intended for people who write or maintain ngGONG documentation and AI agents assisting them.
Style: Instructional and approachable. Use plain language, practical examples, and direct guidance.
-->

# Author's Guide

This guide helps contributors write and update ngGONG documentation for its intended readers.
The guidance also applies to AI agents assisting with those changes.

## Purpose, Audience, and Style

Before writing or revising a document, establish three things:

1. [Define the document's purpose](#define-the-purpose): What is it for, and what does it cover?
2. [Identify the audience](#identify-the-audience): Who needs it, and what do they need from it?
3. [Choose the writing style](#choose-the-writing-style): How should the content be presented to serve that purpose and audience?

Documentation may be edited by people and AI agents who do not share the original author's context.
A purpose, audience, and style (PAS) ***comment block*** records the document's intended role so contributors and reviewers
can judge whether a change belongs and how to present it.
Keeping this context in the source helps preserve that intent across edits without adding authoring guidance to the
published document.
Keeping authoring guidance separate reduces distractions for readers.
Selected information about purpose, audience, or style may still be useful in the published document
when it helps readers understand or use the content.
In those cases include both a comment block with the information and the relevant information in the published content.

### Define the Purpose

Identify what the document explains, specifies, or helps readers do.
State its scope and the outcome it should support for readers.
For an existing document, confirm its intended role before deciding whether new content belongs in it.
If its purpose is unclear, discuss it before choosing a new scope.

### Identify the Audience

Identify the primary readers and what they need from the document.
Include secondary audiences when their needs affect its content or presentation.
Potential audiences include:

- **Reviewers:** Assess the design, requirements coverage, or project approach.
- **Project developers:** Implement, test, or maintain software.
- **Operations and maintenance personnel:** Understand station behavior and operational procedures.
- **Documentation contributors:** Create and maintain the document set.
- **AI agents:** Perform tasks using the document's information or guidance.

These are examples rather than fixed categories.
Describe the readers the document serves rather than listing every possible audience.

### Choose the Writing Style

Style depends on what the document does, not just how formal it looks.
Use the following patterns as a starting point and describe the approach that fits the particular documentation source.

| Document role | Typical examples | Writing approach |
| --- | --- | --- |
| Informational overview | Repository index | Plain, descriptive prose that explains and directs readers. |
| Design description | Conceptual design | Precise technical explanation of structure, decisions, rationale, and open questions. |
| Specification or plan | Policy specification, development plan | Precise rules or commitments; normative language for obligations. |
| Instructional guide | Developer how-to | Direct steps, commands, examples, and explanations. |

Informative content explains; normative content establishes obligations.
A document may contain both, so its style description can identify where each applies.
For example, a specification can contain mandatory rules alongside descriptive context and rationale.

Use "shall" for mandatory rules or commitments.
Keep context and rationale descriptive, including in formal documents.
An informational overview does not need normative language to explain the document set.

### Write the Comment

Record the purpose, audience, and style in a comment at the top of the documentation source.
PAS comments apply only to Markdown (`.md`) and Quarto (`.qmd`) sources that form the
document set, including landing pages, guides, formal documents, and included document sections.
Configuration files such as `_quarto-website.yml`, scripts, build files, templates, and agent instruction files are outside
this scope, even when a support file uses Markdown.

Before editing a documentation source, read its purpose comment and keep changes consistent with the stated purpose,
audience, and style.
An intentional change to that scope also needs a matching update to the comment.
If the purpose or audience is unclear, discuss it before choosing a new scope.

When creating a documentation source covered by this guidance, add a purpose comment.
When updating one that lacks a comment, add a comment that reflects its existing purpose, audience, and style.
If a comment already describes purpose and audience but lacks style guidance, add the style description.

Use these three labels:

- **Purpose:** One or two sentences explaining what the documentation source contains and what it is for.
- **Audience:** One sentence identifying its intended readers, such as reviewers, project developers, or AI agents.
  These are examples rather than a fixed list of audiences.
- **Style:** A short description of the expected writing approach and whether the content is informative, normative,
  or a mixture.

Use an HTML comment for Markdown and Quarto documents, as in this example:

```html
<!--
Purpose: Explain how to preview repository documentation locally.
Audience: This guide is intended for project developers and documentation contributors.
Style: Instructional and direct. Use short steps, commands, and examples.
-->
```

If a documentation source has leading YAML metadata, keep that metadata first and place the purpose comment immediately
after it.

## Preview Changes

Use the [documentation preview guide](docker-preview.md) to set up and run a local preview.
Check the rendered page as well as the source, especially after changing links, headings, tables, or navigation.
