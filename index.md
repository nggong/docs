<!--
Purpose: Introduce this repository at a high level and explain what documentation is present and what each document is for.
It also describes how the document set relates to external project documents.
Audience: This page is intended for project developers, reviewers, and other readers seeking an overview of the documentation.
Style: Informational and descriptive. Use plain language to explain the document set and help readers navigate it.
-->

# Overview

[The Next-Generation Ground-based Solar Observatory Network](https://nso.edu/telescopes/nggong)
is a geographically distributed network of six solar observing stations designed to provide continuous observations of the Sun.
Each station operates largely autonomously, while High Level Software, Controls, and Data Management work together to
operate the telescopes, monitor the network, acquire observations, and deliver data for fundamental science and space weather.

This website (and backing github repository) contains the ngGONG software documentation.
The primary audience for this documentation is developers of ngGONG software but it may be relevant
to others, especially reviewers.

For guidance on writing and updating this documentation, see the
[Author's Guide](docs/developer-guides/authors-guide.md).

## Document Relationships and Source Authority

This section is the shared reference for how documents in this repository relate to each other and to external
ngGONG project documents.
Authority depends on the scope, allocation, and approval status of a source, not on whether it is stored in this repository.
Approved requirements, allocations, and interface contracts constrain the design and operational details in this repository.
Draft or proposed content does not by itself indicate project approval.

### External Project Documents

The following document types provide requirements, constraints, and operational context for the software documentation.

| Document | Role |
| --- | --- |
| Operational Concepts Document (OCD) | Observatory operational intent, scenarios, and nominal and off-nominal behavior. |
| Operational Architecture Document (OAD) | System responsibilities, functional allocations, boundaries, and interfaces. |
| Science Requirements Document (SRD) | Science drivers, performance requirements, and science-data-product requirements. |
| Design Requirements Documents (DRDs) | Requirements allocated to individual systems, including software and controls. |
| Interface Control Documents (ICDs) | Contracts between systems or components. |

### Documents in This Repository

The documents in this repository develop different parts of the software definition:

- The **Software Development Plan** defines the software development, verification, and maintenance approach.
- The **Software Design Description** develops software responsibilities, boundaries, interactions, and design decisions
  consistent with the applicable requirements and system allocations.
- Various **Interface Control Documents (ICDs)** describing the interface between different elements of the Software.
- **Supporting specifications and guides**, including release and deployment guidance, develop details within their
  stated scope and remain consistent with the applicable requirements, design, and development plan.

Upstream documents are not expected to contain every detail needed for design, implementation, operation, or verification.
Repository documents provide agreed details within their allocated scope that need not first appear in an upstream document.
For example, the SCS-OPWS supplies policy and workflow detail that requirements and conceptual design leave open.
Those requirements and allocations continue to govern the resulting details.
Proposed content and items marked **TBD** represent decisions that are not yet settled.
