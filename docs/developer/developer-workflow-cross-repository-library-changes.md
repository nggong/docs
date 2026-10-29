# Developer Workflow for Cross-Repository Library Changes

For the proposed automation supporting this workflow, see
[GitHub Automation for Cross-Repository Library Changes](github-cross-repository-library-workflows.md).
For release policy, see [SCS Release and Deployment Management](../hls/scs/release-and-deployment-management.md).

This workflow applies when a change modifies a reusable Maven library in one repository and an application that consumes that library in another repository. It assumes both repositories are already cloned and configured to use the required Maven package repository.

The examples use:

```text
Library repository directory:     observation-protos
Application repository directory: scs-acquisition
Maven coordinate:                 org.nggong:observation-protos
Application version property:     nggong.observation-protos.version
```

The examples assume GitHub Packages and a committed `ci/maven-settings.xml` in each repository, adapted from the
[reference settings file](maven-settings.xml).
Its URL identifies the library's publishing repository in both the library and application checkouts.
Set `MAVEN_USERNAME` to your GitHub username and supply `MAVEN_TOKEN` through your local credential mechanism as a personal
access token (classic) with the package read access needed for these builds.
Maven reads the settings file explicitly through `-s`; actual credentials remain outside Git.

## 1. Create the Development Branches

Create the library branch from the current default branch:

```bash
cd observation-protos
git fetch origin
git switch main
git pull --ff-only
git switch -c add-observation-start-time
```

Create the related application branch:

```bash
cd ../scs-acquisition
git fetch origin
git switch main
git pull --ff-only
git switch -c use-observation-start-time
```

Use the project's branch-naming policy if it defines a required issue number or prefix.

## 2. Change and Build the Library Locally

Return to the library repository and edit the `.proto` definitions and their tests:

```bash
cd ../observation-protos
```

The library POM uses the default local version:

```xml
<version>${revision}</version>

<properties>
    <revision>0.0.0-local-SNAPSHOT</revision>
</properties>
```

Build, test, and install the library into the local Maven repository:

```bash
mvn -s ci/maven-settings.xml clean install
```

The resulting local coordinate is:

```text
org.nggong:observation-protos:0.0.0-local-SNAPSHOT
```

Do not publish this version. It is meaningful only on the developer's workstation.

## 3. Develop and Test the Application Locally

Move to the application repository:

```bash
cd ../scs-acquisition
```

Keep the committed application POM on the latest official library version while doing initial local work. Override it from the command line:

```bash
mvn \
    -s ci/maven-settings.xml \
    -Dnggong.observation-protos.version=0.0.0-local-SNAPSHOT \
    clean verify
```

When the library changes again, rerun `mvn -s ci/maven-settings.xml clean install` in the library repository and then
rerun the application build.

Confirm the selected dependency when troubleshooting:

```bash
mvn \
    -s ci/maven-settings.xml \
    -Dnggong.observation-protos.version=0.0.0-local-SNAPSHOT \
    dependency:tree \
    -Dincludes=org.nggong:observation-protos
```

Do not copy the JAR into the application repository, use `systemPath`, or add a local filesystem repository to the POM.

## 4. Commit and Push the Library Change

Commit the library change first:

```bash
cd ../observation-protos
git status --short
git add <changed-files>
git commit -m "Add observation start time to status message"
git push -u origin add-observation-start-time
```

Open the library pull request. Record its number; the examples below use PR `417`.

The library PR workflow calculates and publishes:

```text
0.0.0-pr.417-SNAPSHOT
```

The version is known as soon as the PR number is assigned. The artifact becomes available only after the publishing workflow succeeds.

The workflow summary should show the exact Maven coordinate. If necessary, inspect the PR checks before continuing.

## 5. Change the Application to the Temporary PR Version

Return to the application repository:

```bash
cd ../scs-acquisition
```

Update the application dependency property for PR integration:

```diff
-<nggong.observation-protos.version>2.3.1</nggong.observation-protos.version>
+<nggong.observation-protos.version>0.0.0-pr.417-SNAPSHOT</nggong.observation-protos.version>
```

Run the application build with Maven's snapshot-update option:

```bash
mvn -s ci/maven-settings.xml -U clean verify
```

You do not have to wait for the library workflow before writing or pushing the application code. If application CI starts before the temporary artifact is published, its dependency-resolution step can fail. Wait for the library publishing check and rerun the application check. Do not add unbounded polling to the build.

## 6. Commit and Push the Application Change

```bash
git status --short
git add <changed-files> pom.xml
git commit -m "Use observation start time from status message"
git push -u origin use-observation-start-time
```

Open the application pull request as a draft. Put a machine-readable dependency marker in its description:

```text
Depends-On: nggong/observation-protos#417
```

Also explain in normal prose:

- why the library change is needed;
- how the application uses it;
- which tests exercise the combined behavior; and
- that the temporary dependency will be replaced automatically after the library release.

After the application PR receives its number, add a back-link to the library PR:

```text
Downstream-PR: nggong/scs-acquisition#892
```

The project may later automate this registration. Until then, treat the two markers as required PR metadata.

## 7. Review the Pull Requests Together

Request review on both PRs at the same time. The intended review state is:

```text
Library PR
    schema/API change
    compatibility result
    proposed Semantic Version class

Application PR
    consuming code
    application behavior
    integration-test result
```

The application PR's integration tests may pass with the temporary library version. Its `release-dependencies` merge check shall remain failed because `0.0.0-pr.417-SNAPSHOT` is not a release dependency.

This failure is intentional. It prevents premature merge without preventing review and integration testing.

## 8. Update the Library PR When Necessary

If review changes the library PR:

1. Commit and push the library updates.
2. Wait for `0.0.0-pr.417-SNAPSHOT` to be republished.
3. Rerun application CI with Maven snapshot updates enabled.
4. Repeat local testing if the generated API or defined behavior changed.

Because the temporary version is scoped to the PR rather than the commit, the application POM does not change for every library revision.

The applicable test record should retain the library head commit that was tested even though the Maven snapshot coordinate is mutable.

## 9. Merge and Release the Library

After both PRs are approved, merge the library PR first.

The library release workflow shall:

1. determine and validate the final Semantic Version;
2. create or verify the matching Git tag;
3. build and publish the immutable JAR;
4. send the final version to the linked application repository; and
5. record the release and its source revision.

For example:

```text
Git tag:       v2.4.0
Maven version: org.nggong:observation-protos:2.4.0
```

Do not manually create a different Maven version in the application repository.

## 10. Verify the Automated Application Update

The application automation should add a commit to the existing PR:

```diff
-<nggong.observation-protos.version>0.0.0-pr.417-SNAPSHOT</nggong.observation-protos.version>
+<nggong.observation-protos.version>2.4.0</nggong.observation-protos.version>
```

Verify that:

- the final JAR exists in the configured Maven repository;
- the automation changed only the expected dependency property;
- the application build uses `2.4.0` without a command-line override;
- the integration tests pass;
- the `release-dependencies` required check passes; and
- the PR no longer contains unresolved dependency metadata.

Do not merge if the automatic updater failed. Fix or rerun the updater rather than manually bypassing the required check.

## 11. Merge the Application PR

After the final-version commit and all required checks pass, mark the application PR ready and merge it according to the repository's normal policy.

The application CI pipeline may then create an application container with a CI-generated build identifier such as:

```text
20261007.4387291542.1
```

The container metadata or SBOM records that it contains:

```text
org.nggong:observation-protos:2.4.0
```

The SCS release manifest later identifies the exact container digest selected for system testing and promotion.

## Failure and Recovery Cases

### The temporary library publication fails

Keep the application PR in draft. Fix the library workflow and rerun it. Do not publish a manually named shared artifact to work around the failure.

### The library PR is closed without merge

Close or revise the dependent application PR. It must not retain the temporary dependency. The temporary artifact becomes eligible for cleanup after the retention grace period.

### The final release fails

The application PR remains blocked by the `release-dependencies` check. Repair the release workflow and complete publication before updating or merging the application.

### The final version updater fails

The automation should comment on the application PR with the validation failure. Correct the metadata or automation and rerun it. A human may update the version only under a documented recovery procedure, followed by the full required test suite.

### More than one application consumes the library change

Open and link a PR in each affected application repository. The library release event shall be sent to every registered consumer. Each application remains independently blocked until its final dependency update and tests succeed.

## Rules Developers Must Not Bypass

- Do not merge an application PR that references `-SNAPSHOT` or `0.0.0-pr.*`.
- Do not use a mutable PR artifact in an SCS candidate or release manifest.
- Do not overwrite a published Semantic Version.
- Do not edit a Git release tag to point to different content.
- Do not assume a major version increase makes a breaking interface change operationally safe.
- Do not delete a temporary artifact while an open application PR still references it.
