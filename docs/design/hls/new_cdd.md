# ngGONG High Level Software Conceptual Design Document

**Project:** Next-Generation Ground-based Solar Observing Network (`ngGONG`)  
**Document:** High Level Software Conceptual Design Document (`HLSCDD`)  
**Review Context:** Conceptual Design Review (`CoDR`)  
**Status:** Draft  
**Author:** John Hubbard  

## Document Purpose

This document describes the conceptual design for ngGONG High Level Software
(`HLS`). It focuses on the software architecture, major subsystems,
responsibilities, key design decisions, logical decomposition, deployment
concept, major communication paths, external interfaces, and technical risks.

The goal of this document is to provide enough architectural clarity for CoDR
reviewers to determine whether:

- The HLS team understands the problem.
- The proposed architecture is sound.
- The major software risks have been identified.
- The architecture can realistically be carried into Preliminary Design Review
  (`PDR`).

## Scope

### In Scope

High Level Software (`HLS`) covers the software responsible for observatory-level
coordination, station-level operation, and the high-level interfaces needed to
operate ngGONG as a six-station observing network.

The two primary HLS subsystems are:

- The Observatory Control System (`OCS`), which runs at a central location such
  as National Solar Observatory headquarters in Boulder or in a cloud-hosted
  environment.
- The Station Control System (`SCS`), with one SCS instance responsible for
  operating each ngGONG station.

In addition to the HLS control systems, the Continuous Integration and Delivery
(`CI/CD`) pipeline is an important part of the overall software effort.

The OCS sends high-level intent to each SCS instance. These commands are
expected to express operational intent rather than low-level device behavior. An
example is an instruction to shut down a station because of an incoming
hurricane.

Each SCS instance is responsible for operating its station and reporting
observatory-relevant information back to the OCS. This includes telemetry,
health and status information, alarms, and logging information so OCS users can
monitor the system as a whole.

HLS includes the high-level software interfaces to:

- Humans using the OCS to monitor and operate ngGONG.
- Controls, which is broadly responsible for the Programmable Logic Controller
  (`PLC`) systems and low-level control of station hardware. HLS uses this
  interface to command motors and other hardware devices.
- The Data Management System (`DMS`), through which HLS offloads data acquired
  at each station. DMS is responsible for final data reduction, distribution, and
  making data available to science and other consumers.

HLS is expected to perform limited station-side data handling or reduction where
needed for operations or data acquisition, such as coadding accumulated camera
frames. HLS is not responsible for producing science-ready data products.

At CoDR, this document should show that the main HLS boundaries are understood,
that the architecture can support six stations and continuous 24/7 operation,
that station autonomy is feasible, that the major external interfaces have been
identified, and that key architectural risks are being driven down.

### Out of Scope

The HLS Detailed Requirements Document (`HLS DRD`) defines the high-level
software requirements. Requirements should be referenced or traced here where
needed, but not repeated in full.

The Operations Concept Document (`OCD`) describes operational concepts and major
operational scenarios, including startup, observing, calibration, maintenance,
fault handling, and disconnected station operations. This document should
reference those scenarios where they affect architecture, but should not repeat
the operational concept in full.

The following items are out of scope for this CoDR-level document and belong at
PDR or later unless a limited conceptual example is needed:

- Production of science-ready data products.
- Low-level servo control, which is the responsibility of Controls.
- Detailed DDS topic definitions.
- Complete protobuf definitions.
- Detailed APIs.
- Complete Interface Control Documents (`ICDs`).
- Detailed state machines.
- Database schemas.
- Deployment scripts.
- Cybersecurity implementation details.
- Exhaustive verification matrix.

## Design Drivers

The HLS architecture is driven by the need to operate ngGONG as a distributed,
largely autonomous observing network. The following drivers shape the conceptual
design.

### Continuous Six-Station Observing

ngGONG will operate six geographically distributed observing stations in order
to observe the Sun continuously. HLS must support routine, day-after-day
operation at each station while allowing the OCS to monitor the health and
status of the full network.

### Station Autonomy

Each station must be able to continue operating for an extended period without
communication to the OCS. The current assumption is that a station should be able
to operate independently for weeks or longer, pending confirmation by OCD
requirements.

This autonomy implies that the SCS must be able to continue routine operations,
recover from basic problems, retain acquired data locally when DMS is
unreachable, and resume orderly data offload when connectivity is restored.

### Supervisory OCS Role

The OCS is expected to be supervisory rather than an active coordinator of
observing activity across stations. Each station should perform its normal work
with little outside input. The OCS provides network-level visibility and can send
high-level operational intent, but routine observing should not depend on
continuous OCS coordination.

### Data Retention and Offload

Loss of communication with the OCS is expected to coincide with loss of access
to DMS in many cases. HLS therefore needs a station-side data retention strategy
and a way to prioritize data offload ordering when connectivity is restored.
The detailed retention policy and prioritization rules are TBD.

### Reliability and Recovery

Quantitative reliability and availability goals have not yet been defined. At
the conceptual design level, the architecture should support recovery from basic
problems and avoid unnecessary dependence on continuous central connectivity.
The current assumption is that full redundancy across the entire control system
is not required.

### Maintainability and Evolution

The HLS architecture must be maintainable across a long system lifetime and
evolve from conceptual design through PDR and implementation. Architectural
choices should preserve clear subsystem boundaries, support incremental risk
reduction, and leave room for requirements that are still being developed.

## Architecture Overview

The top-level HLS architecture is station-autonomous. Each ngGONG station is
expected to carry out routine observing and station operation with little
outside input. The central OCS provides observatory-level monitoring and sends
very high-level commands or operational intent to the stations, but it is not
expected to actively coordinate observing activity across stations.

The main architectural split is between the central OCS and the station-local SCS
instances. The OCS gives users a network-level view of ngGONG and receives
telemetry, health and status information, alarms, and logs from the SCS
instances. The SCS at each station is responsible for local operation, commanding
station hardware through Controls, directing camera acquisition, receiving
camera readouts, performing limited station-side data handling where needed, and
offloading acquired data to DMS.

The OCS-to-SCS interface is expected to carry high-level intent rather than
low-level device commands. The current architectural direction is to use gRPC
for this interface. Detailed service definitions, message schemas, and complete
interface specifications are out of scope for CoDR.

The SCS is expected to be a collection of cooperating software pieces rather
than a single monolithic application. The SCS is substantially more complex than
the OCS and will require additional design detail. That detail may be captured
in an SCS Conceptual Design Document or by expanding the SCS sections of this
HLS CDD.

Software deployment management to the stations may be part of the OCS, but that
responsibility is still TBD.

### System Context

TODO: Add or reference a system context diagram.

The diagram should show ngGONG HLS in relation to the broader ngGONG system,
external systems, operators, engineers, scientists, and data consumers.

### HLS Context

TODO: Add or reference an HLS context diagram.

The diagram should show the boundary of HLS and the major systems with which it
interacts.

### HLS Decomposition

TODO: Add or reference an HLS decomposition diagram.

The diagram should show the primary HLS subsystems and their responsibilities.

## Major Software Components

TODO: Identify and describe the major HLS software components.

For each component, capture:

- Primary responsibility.
- Major inputs and outputs.
- Important dependencies.
- Operational role.
- Key design constraints or open questions.

### Observatory-Level Components

TODO: Describe software components that operate at the observatory level.

The OCS is the primary human interaction point during regular operations. It
will provide operations personnel with per-station status, health, and
telemetry information. It will allow operations staff to send high-level
commands or state requests to individual stations.

### Station-Level Components

TODO: Describe software components that operate at individual ngGONG stations.

The SCS is the station-local HLS system responsible for coordinated,
autonomous operation of an ngGONG telescope station. It presents the station as
a coherent operational system to the OCS while preserving internal authority
boundaries among station software components, hardware-facing controllers,
science-data handling, common services, and independent safety enforcement.

At the conceptual level, each SCS includes a Station Agent, Station Common
Services, and several logical architectural planes. The Station Agent is the
station-level HLS orchestration authority. It receives high-level operational
commands and requested outcomes through the OCS-facing supervisory interface,
validates them against station state and policy, maps accepted requests to
controlled workflows, coordinates the participating station components, and
determines station-level command results.

The logical SCS planes separate supervisory control, station-local state
coordination, device execution, and science-data movement. Common Services
provide shared station capabilities such as security support, configuration,
timing-quality visibility, observability, audit, command tracing, and runtime
or deployment support. These services support station operation but do not
become authoritative for station operational behavior merely by providing
shared infrastructure.

### Shared Services and Libraries

TODO: Describe common services, libraries, frameworks, or utilities expected to
support the HLS architecture.

## Select Sequence Diagrams

TODO: Add a small number of informative sequence diagrams that clarify important
architecture-level behavior.

Candidate sequences:

- Typical observing sequence.
- Fault handling concept.
- Station startup.
- Observatory-to-station coordination.
- Disconnected station operation at a conceptual level.

These diagrams should remain conceptual. Avoid detailed API messages, complete
topic definitions, and implementation-level state transitions.

## Deployment Concept

TODO: Describe the conceptual deployment model for HLS.

This section should address:

- Station deployment concept.
- Observatory deployment concept.
- Major runtime environments.
- Expected deployment boundaries.
- Relationship between deployed components and physical stations.
- High-level operational dependencies.

### Station Architecture

TODO: Add or reference a station architecture diagram.

### Observatory Architecture

TODO: Add or reference an observatory architecture diagram.

### Software Deployment

TODO: Add or reference a software deployment diagram.

## Communication Paths

TODO: Describe the major communication paths used by HLS.

This section should summarize:

- Communication between observatory-level and station-level software.
- Communication between HLS and lower-level control systems.
- Communication between HLS and data systems.
- Communication between HLS and users or operator interfaces.
- Major assumptions about latency, availability, and disconnected operation.

### Communications Overview

TODO: Add or reference a communications overview diagram.

## External Interfaces

TODO: Identify external interfaces at a conceptual level.

This section should describe interface boundaries and responsibilities without
including complete ICDs, detailed APIs, protobuf definitions, or DDS topic
definitions.

Potential interface categories:

- Telescope and instrument control interfaces.
- Observatory control interfaces.
- Data management interfaces.
- Operator and engineering user interfaces.
- Station infrastructure interfaces.
- External monitoring, logging, or alerting interfaces.

## State Model

TODO: Describe the conceptual state model if needed to explain the architecture.

This section should remain high-level. Detailed state machines are out of scope
for CoDR and should be deferred to PDR unless a simplified state model is needed
to explain architectural behavior.

## Major Design Decisions

TODO: Summarize the key architectural decisions made for HLS.

For each decision, include:

- Decision statement.
- Context.
- Alternatives considered.
- Rationale.
- Consequences.
- Open issues, if any.

## Trade Studies

TODO: Include one- or two-page summaries of important trade studies where they
justify architectural decisions.

Each trade study summary should include:

- Question or decision being studied.
- Options considered.
- Evaluation criteria.
- Recommendation.
- Rationale.
- Risks or follow-up work.

## HLS DRD Traceability

TODO: Provide traceability from system-level needs to HLS requirements and then
to major architectural elements.

This section should reference the HLS DRD rather than repeat the full set of
requirements.

Suggested columns:

| System Need | HLS Requirement Reference | Architectural Element | Notes |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Architecture Decision Summary

TODO: Provide a compact summary of the most important architectural decisions.

Suggested columns:

| Decision | Status | Rationale | Related Trade Study | Follow-Up |
| --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | TODO |

## Technical Risks and Mitigations

TODO: Identify major technical risks and planned mitigations.

Suggested columns:

| Risk | Impact | Likelihood | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | TODO | TODO |

## Development Approach

TODO: Describe the planned software development approach at a conceptual level.

The CI/CD pipeline is part of the HLS development approach. At the conceptual
design level, it should support repeatable builds, automated verification,
controlled delivery of software artifacts, and traceability between source
changes, built artifacts, and deployed station or observatory software.

This section may include:

- Development phasing from CoDR toward PDR.
- Prototype or pathfinder work.
- Modeling, simulation, or integration strategy.
- Documentation strategy.
- Risk reduction activities.
- Expected evolution of architecture decisions.

## Open Questions

TODO: Track open architectural and documentation questions that need resolution
before or during CoDR preparation.

Suggested columns:

| Question | Context | Needed By | Owner | Status |
| --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | TODO |

## Appendix A: Candidate Diagrams

The following diagrams are candidates for inclusion if they materially clarify
the conceptual design:

- System context.
- HLS context.
- HLS decomposition.
- Station architecture.
- Observatory architecture.
- Software deployment.
- Communications overview.
- Typical observing sequence.
- Fault handling concept.
- State model.

## Appendix B: CoDR Review Question Checklist

Use this checklist to evaluate whether the document is addressing the expected
CoDR-level concerns:

- Does the document show that the HLS team understands the problem?
- Does the document present a sound architecture?
- Does the document identify the major software risks?
- Does the document show that the architecture can realistically be carried into
  PDR?
