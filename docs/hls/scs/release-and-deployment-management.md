# SCS Release and Deployment Management

## Purpose and Scope

This section defines how ngGONG Site Control System (SCS) build artifacts are identified, assembled into SCS releases, qualified, promoted, deployed, revoked, rolled back, and retained.
The process applies to the SCS and can be adapted for other software systems.

The process separates four concepts that must not be conflated:

1. **Build identity** identifies a specific execution of a component’s build pipeline, including the pipeline run.
2. **Artifact identity** identifies one immutable output produced by a build, such as a container image identified by its registry digest.
3. **Release identity** identifies one tested composition of component artifacts and deployment configuration.
4. **Deployment state** identifies the release currently approved for a channel or station.

Container images and release manifests are immutable.
Names such as `candidate`, `production`, and station-specific deployment channels are mutable pointers to immutable objects.

## Artifact Management

Source code shall be maintained in Git repositories.
Build artifacts shall be published to repositories designed for their artifact type rather than committed to Git.

- Reusable libraries (e.g. a Java .jar) shall be published to a artifact repository (e.g. Maven) when another component consumes them as dependencies.
- Deployable services shall be published as container images to a container registry.
- A service does not need a separately published library unless another component consumes that library.
- System release manifests shall be stored as immutable release artifacts in the SCS deployment repository, such as assets attached to GitHub Releases.

Each successful component build shall receive a unique, immutable build identifier.
A format similar to the following is recommended:

```text
<base-version>-ci.<date>.<run-number>.g<commit>
```

For example:

```text
1.3.0-ci.20260901.184.g4f92ac1
```

Human-readable tags may be used for navigation, but deployment decisions shall use immutable container-image digests.
A tag such as `candidate` may move when a newer eligible build becomes available; a digest such as `sha256:abc123...` identifies fixed content.

Published artifacts should include, when supported by the build and registry infrastructure:

- the source commit identifier;
- build and dependency metadata;
- a software bill of materials (SBOM);
- provenance or build attestations; and
- vulnerability-scan results or a reference to the applicable scan record.

## Component Candidate Selection

Each deployable component shall have its own CI pipeline.
The pipeline shall, at minimum:

1. compile and package the component;
2. run unit and component tests;
3. run static analysis and other required quality and security checks;
4. verify applicable API, message-schema, and interface contracts;
5. build the container image;
6. publish the image under a unique build identifier; and
7. resolve and record the published image digest.

After these checks pass, the component's `candidate` channel may be advanced to the new image digest.
At the component level, `candidate` means only that the artifact passed its own CI and is eligible for inclusion in a system release candidate.
It does not mean that the component has passed SCS system testing or is approved for production.

Interface changes should be additive by default.
Breaking changes shall use an explicit interface-version transition and, when practical, an expand-and-contract sequence that permits old and new component versions to coexist during deployment.
Exhaustive pairwise old/new integration testing is not required for every component build.
Fast contract and schema-compatibility checks shall protect service boundaries in component CI, while assembled-system tests shall run against a fixed SCS composition.

## SCS Release Composition

A dedicated SCS deployment repository shall define deployment configuration and create system release candidates.
On a scheduled trigger (daily), or on an authorized manual trigger, its release-composition pipeline shall:

1. identify the current eligible candidate for each required SCS component;
2. resolve every candidate tag or channel to an immutable image digest;
3. identify the exact deployment-configuration revision;
4. generate an immutable SCS release manifest;
5. assign the manifest a unique SCS release identifier;
6. archive the manifest before deployment;
7. advance the SCS `candidate` channel to the new release identifier; and
8. request deployment of that release to the test environment.

The pipeline shall fail rather than create an incomplete manifest when a required component cannot be resolved or its provenance cannot be verified.

An SCS release identifier may use a date and sequence number, for example:

```text
2026.09.01.01
```

Once assigned, a release identifier shall never be reused for different content.

### Release Manifest Contents

The release manifest is the system-level release artifact.
It declares the exact content that was tested; it is not a copy of the component images.
At minimum, it shall record:

- the SCS release identifier;
- the creation time and creating pipeline run;
- the source revision of the deployment repository;
- every component name, image location, image digest, build identifier, and source revision;
- the deployment-configuration revision;
- applicable configuration-schema and database-migration levels;
- references to SBOMs, attestations, and other provenance records where available; and
- manifest format or schema version.

For example:

```yaml
schema_version: 1
release: 2026.09.01.01
created: 2026-09-01T22:00:00Z
deployment_revision: 71bd8af

components:
  acquisition:
    image: ghcr.io/nggong/scs-acquisition@sha256:aaa...
    build: 1.4.0-ci.20260901.184.g4f92ac1
    source_revision: 4f92ac1

  sa:
    image: ghcr.io/nggong/scs-sa@sha256:bbb...
    build: 2.1.0-ci.20260901.91.gab12c34
    source_revision: ab12c34

  transfer:
    image: ghcr.io/nggong/scs-transfer@sha256:ccc...
    build: 1.8.0-ci.20260901.227.g9981def
    source_revision: 9981def

configuration:
  schema: 3
  database_migration: 17
```

The manifest schema shall be machine-validated.
Its canonical content should also be signed or covered by a repository or release attestation.

## Qualification and Promotion

The test environment shall consume the SCS `candidate` channel and deploy the exact release manifest referenced by that channel.
It shall not independently select the latest component images.

System qualification shall include the applicable integration, system, operational, upgrade, and regression tests.
Qualification results shall be associated with the exact SCS release identifier and manifest digest.
New component candidates published while qualification is in progress shall not alter the release under test; they are eligible only for a later composition.

If qualification fails:

- the release shall not be promoted;
- the failed manifest and results shall be retained for traceability;
- the SCS `candidate` channel may advance to a later corrected release; and
- no component image or release manifest shall be changed in place.

If qualification succeeds, an authorized promotion workflow shall advance the `production` channel to the qualified release identifier.
The workflow shall promote the same manifest and image digests that passed testing.
It shall not rebuild the component images or generate a replacement manifest.

Promotion is therefore a deployment-state change:

```text
candidate  -> 2026.09.01.02
production -> 2026.09.01.01
```

It is not a change to the artifacts referenced by either release.

## Deployment Channels

A deployment channel is a mutable, version-controlled pointer to an immutable release manifest.
The deployment repository or an NSO-controlled deployment service derived from it shall be the authoritative source of channel state.

The project shall not use GitHub's `latest` release designation, a container `latest` tag, or lexicographic sorting of release names as the production-approval mechanism.
Stations shall request the release explicitly approved for their applicable channel.

The channel model should allow a global production release and controlled exceptions, for example:

```yaml
production:
  release: 2026.09.01.01

station_overrides:
  mauna-loa:
    release: 2026.08.29.01
    reason: maintenance-hold

revoked:
  - release: 2026.08.30.01
    reason: NGGONG-1234
```

Changes to production and station-specific channels shall be authenticated, authorized, auditable, and recoverable through version history.
Normal promotion should use the standard review process.
A documented emergency process shall permit an authorized operator to revoke or roll back a release without waiting for the normal release schedule.

## Station Deployment

Each station shall periodically obtain signed or authenticated deployment state from the authoritative source.
A station deployment agent shall:

1. retrieve the release approved for the station's applicable channel;
2. retrieve the current revocation state;
3. compare the approved release with the locally installed release;
4. verify the release manifest, provenance, and referenced image digests;
5. stage required artifacts without changing the running system, where practical;
6. deploy during a locally appropriate operational window;
7. run required post-deployment health checks; and
8. report and retain the installed release identifier and deployment result.

Stations shall deploy only artifacts named by the approved release manifest.
They shall not follow component-level `candidate`, `production`, or `latest` tags.

A station shall not deploy solely from a stale cached production pointer.
Before starting a deployment, it shall confirm that the selected release remains approved and is not revoked.
If current authorization state cannot be obtained, the default behavior shall be to keep the installed release rather than begin a new deployment.
The project shall define any controlled exception needed for extended network outages.

## Revocation and Rollback

Promotion, revocation, and rollback are separate operations:

- **Promotion** advances a deployment channel to a newly qualified release.
- **Revocation** declares that a release must not receive future deployments.
- **Rollback** changes desired or installed state to a prior known-good release.

If a production release is found to be defective after one or more stations deploy it, the incident response shall:

1. mark the affected release as revoked and record the reason and incident reference;
2. move the production channel to the last known-good release;
3. publish the updated channel and revocation state immediately;
4. identify stations that downloaded, staged, or installed the revoked release;
5. cancel pending deployments of the revoked release;
6. direct affected stations to roll back when rollback is safe;
7. preserve the revoked release manifest, images, evidence, and deployment history;
8. correct the affected component through its normal build pipeline; and
9. compose and fully qualify a new SCS release.

The revoked release shall not be deleted or modified.
Its release notes or external status metadata may identify it as revoked, but its tag, manifest, and attached artifacts shall remain unchanged.

For a GitHub-based implementation, immutable GitHub Releases may hold the release manifests.
Mutable channel and revocation state should remain as version-controlled files or be published by a deployment service.
An emergency rollback changes `channels/production.yaml` to the previous release and adds the defective release to the revocation record.
The change is then committed, reviewed under the emergency procedure, merged, and published to stations.
GitHub's `latest` release indicator shall not be treated as the channel pointer.

Rollback shall not be assumed to be safe for stateful components.
Database migrations, persisted data formats, protocol state, and external controller configuration can prevent a simple return to old containers.
Each stateful component shall declare one of the following for every release transition:

- rollback to the previous production release is supported;
- rollback requires restoration of identified state or data; or
- rollback is not supported and recovery requires a forward fix.

Irreversible migrations require an approved recovery plan before promotion.

## Retention and Pruning

Artifact pruning shall be based on reachability and operational need, not only artifact age.

The retention process shall protect:

- every artifact referenced by a candidate, production, station-specific, or other active channel;
- every artifact referenced by an immutable release manifest retained under the project records policy;
- the release currently installed or staged at each station;
- at least the configured number of prior known-good releases needed for rollback;
- revoked releases and artifacts required for incident analysis; and
- artifacts subject to a legal, security, audit, or milestone hold.

Unreferenced component candidates that never entered a release manifest may be deleted after a defined grace period.
Temporary build products and CI logs may use shorter retention periods if they are not required to reproduce or audit a release.
Registry garbage collection shall run only after the reachability calculation and grace period are complete.

Deleting a mutable tag does not necessarily delete image content, and deleting image content can break an old release even when its manifest remains.
The pruning process shall therefore work from immutable digests and shall verify that no protected manifest or deployed station references an artifact before deletion.

Retention durations, the rollback depth, and the treatment of milestone releases shall be defined in the project records and configuration-management policies.
These values remain **TBD** until those policies are approved.

## Traceability and Audit Records

The release process shall make it possible to determine:

- which source revisions produced each component artifact;
- which artifact digests formed each SCS release;
- which deployment configuration was applied;
- which tests qualified the release and their results;
- who or what promoted, revoked, or rolled back the release;
- which release each station installed and when; and
- whether deployment and post-deployment checks succeeded.

Release, channel, test, and station-deployment records shall use stable identifiers so that records can be correlated across Git, CI, artifact registries, the deployment service, and observability systems.

## Roles and Responsibilities

Specific organizational assignments remain **TBD**, but the following responsibilities shall be assigned:

- **Component maintainers** maintain component CI, interface contracts, artifact metadata, and component rollback declarations.
- **Release automation** composes and validates immutable SCS release manifests.
- **Test authority** defines qualification criteria and accepts or rejects a release candidate.
- **Release authority** approves production promotion and emergency channel changes.
- **Station operations** control local deployment windows and respond to failed deployments.
- **Configuration management** maintains release records, retention rules, and auditability.

No single mutable tag or unrecorded runtime state shall be the only evidence of what was tested, approved, or deployed.
