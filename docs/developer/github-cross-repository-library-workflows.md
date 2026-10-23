# GitHub Automation for Cross-Repository Library Changes

## Purpose

For the developer procedure, see
[Developer Workflow for Cross-Repository Library Changes](developer-workflow-cross-repository-library-changes.md).
For release policy, see [SCS Release and Deployment Management](../hls/scs/release-and-deployment-management.md).

This guide describes a proposed GitHub Actions implementation for changes that span:

- a repository that publishes a reusable Maven library, such as a JAR generated from Protocol Buffer definitions; and
- one or more application repositories that consume that library and publish container images.

The design has four objectives:

1. Let developers test related changes before the library has a final release.
2. Let reviewers see the library and application changes at the same time.
3. Replace temporary PR dependencies automatically after the library is released.
4. Prevent an application PR from merging while it references a temporary or snapshot dependency.

The examples use these placeholders:

```text
Library repository:     nggong/observation-protos
Application repository: nggong/scs-acquisition
Maven coordinate:       org.nggong:observation-protos
Maven property:         nggong.observation-protos.version
```

Replace them with the actual repository names and Maven coordinates during implementation.

## Resulting Lifecycle

```text
Library PR #417
    -> publish 0.0.0-pr.417-SNAPSHOT
    -> application PR #892 consumes temporary version
    -> both PRs reviewed together
    -> library PR merged
    -> publish final version 2.4.0
    -> dispatch release event to consumer repository
    -> automation updates application PR to 2.4.0
    -> required release-dependency check passes
    -> application PR may merge
```

Temporary PR artifacts are mutable integration aids. Final Semantic Version releases and application container digests are immutable.

## Prerequisites

Before implementing the workflows:

1. Configure GitHub Packages as the Maven artifact repository.
2. Configure the library repository to publish Maven packages.
3. Configure application repositories to read the package.
4. Configure release versions so they cannot be overwritten.
5. Create a narrowly authorized GitHub App for cross-repository automation.
6. Add branch rules that require the application integration tests and the release-dependency check.
7. Decide the retention period for temporary `0.0.0-pr.*-SNAPSHOT` artifacts.

Relevant GitHub documentation:

- [Working with the Apache Maven registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry)
- [Publishing Java packages with Maven](https://docs.github.com/en/actions/tutorials/publish-packages/publish-java-packages-with-maven)
- [Publishing and installing packages with GitHub Actions](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)
- [Configuring package access control and visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

## Configure the Library POM

Use a Maven CI-friendly version placeholder so normal development does not edit a shared release number:

```xml
<version>${revision}</version>

<properties>
    <revision>0.0.0-local-SNAPSHOT</revision>
</properties>
```

With Maven 3, configure the Flatten Maven Plugin so installed and deployed POMs contain resolved, consumable versions. Select and pin the plugin version according to the project's dependency-management policy.

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>flatten-maven-plugin</artifactId>
    <version>${flatten-maven-plugin.version}</version>
    <configuration>
        <flattenMode>resolveCiFriendliesOnly</flattenMode>
        <updatePomFile>true</updatePomFile>
    </configuration>
    <executions>
        <execution>
            <id>flatten</id>
            <phase>process-resources</phase>
            <goals>
                <goal>flatten</goal>
            </goals>
        </execution>
        <execution>
            <id>flatten-clean</id>
            <phase>clean</phase>
            <goals>
                <goal>clean</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

References:

- [Maven CI-Friendly Versions](https://maven.apache.org/guides/mini/guide-maven-ci-friendly.html)
- [Flatten Maven Plugin](https://www.mojohaus.org/flatten-maven-plugin/)

The library's default local coordinate is therefore:

```text
org.nggong:observation-protos:0.0.0-local-SNAPSHOT
```

The release pipeline overrides `${revision}` without modifying the POM:

```bash
mvn -s ci/maven-settings.xml -Drevision=2.4.0 clean deploy
```

## Publish a Temporary Artifact for Each Library PR

### Committed Maven Settings for GitHub Packages

Copy the reference [maven-settings.xml](maven-settings.xml) to `ci/maven-settings.xml` in the library and application
repositories and commit it there.
Replace the illustrative `observation-protos` repository name with the actual library repository.
Maven reads this file when a command supplies `-s ci/maven-settings.xml`.
No setup script or generated settings file is required.

The file specifies where Maven downloads library dependencies, enables releases and snapshots, and associates the
repository ID `github` with credentials supplied through environment variables.
Maven Central remains available through Maven's default configuration.
The library POM separately selects the publication destination, using the same credential ID:

```xml
<distributionManagement>
    <repository>
        <id>github</id>
        <url>https://maven.pkg.github.com/nggong/observation-protos</url>
    </repository>
</distributionManagement>
```

For library publication, configure these variables at job scope so all Maven steps receive the credentials:

```yaml
env:
  MAVEN_USERNAME: ${{ github.actor }}
  MAVEN_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Library publication requires `packages: write` and access to the package in the publishing repository.
Application CI needs package read access: use its `GITHUB_TOKEN` with `packages: read` if it has the required package access,
or supply an authorized personal access token (classic) with `read:packages` through a secret.
Local developers supply their GitHub username and a personal access token (classic) through these environment variables.
Actual credential values shall not be committed to the settings file.
GitHub App tokens used for branch updates are separate from Maven package credentials.
See [GitHub's Maven registry authentication guidance](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry).

Select the approved Java Development Kit (JDK) and install Maven before the Maven steps.
The example uses repository variables for the Java distribution and version; their actual values remain **TBD**.
Any settings generated by the Java setup action are unused because each Maven command selects the committed file explicitly.
See the [Maven settings reference](https://maven.apache.org/settings.html) for environment interpolation and other settings.

### Publishing Workflow

Create a pull-request workflow in the library repository. It should run for `opened`, `synchronize`, and `reopened` events and calculate:

```text
0.0.0-pr.<pull-request-number>-SNAPSHOT
```

For example:

```text
0.0.0-pr.417-SNAPSHOT
```

The PR number is available as `github.event.pull_request.number`. When the workflow needs the actual source commit, use `github.event.pull_request.head.sha`; `github.sha` normally identifies GitHub's synthetic PR merge commit.

Illustrative workflow:

```yaml
name: Publish PR Maven artifact

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  packages: write
  pull-requests: read

concurrency:
  group: ${{ github.workflow }}-pr-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  publish:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    env:
      MAVEN_USERNAME: ${{ github.actor }}
      MAVEN_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    steps:
      - uses: actions/checkout@v5
        with:
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Set up Java
        # Configure these variables with the organization-approved toolchain.
        # Maven must also be installed on the runner before the build steps.
        uses: actions/setup-java@v4
        with:
          distribution: ${{ vars.JAVA_DISTRIBUTION }}
          java-version: ${{ vars.JAVA_VERSION }}

      - name: Calculate temporary version
        id: version
        env:
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          version="0.0.0-pr.${PR_NUMBER}-SNAPSHOT"
          echo "version=${version}" >> "$GITHUB_OUTPUT"
          echo "Temporary Maven version: \`${version}\`" >> "$GITHUB_STEP_SUMMARY"

      - name: Build and test
        run: >
          mvn
          -s ci/maven-settings.xml
          -Drevision=${{ steps.version.outputs.version }}
          clean verify

      - name: Confirm this run still matches the PR head
        env:
          GH_TOKEN: ${{ github.token }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          EXPECTED_SHA: ${{ github.event.pull_request.head.sha }}
        run: |
          current_sha="$(gh api \
            "repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}" \
            --jq '.head.sha')"
          if [ "$current_sha" != "$EXPECTED_SHA" ]; then
            echo "PR head changed; refusing to publish this superseded build."
            exit 1
          fi

      - name: Publish
        run: >
          mvn
          -s ci/maven-settings.xml
          -Drevision=${{ steps.version.outputs.version }}
          deploy
```

The concurrency group is scoped to the workflow and PR.
A new run for the same PR cancels the running build and supersedes any pending run.
Different PRs may build concurrently.
The head-commit check prevents a superseded build from starting the publication step if cancellation has not reached it yet.
If the head lookup fails, the step fails and publication does not proceed.

Cancellation cannot undo an upload already in progress.
A new commit can also arrive after the head check, so these controls reduce the race without guaranteeing that a mutable
snapshot always represents the latest PR head.
Application CI shall retain the library source revision it tested, as described in the developer workflow.
If exact PR-build identity is required, use the commit-specific temporary version model below and have consumers select
the exact version they test.

The workflow must not publish untrusted code from forked PRs with write credentials. The `if` guard above restricts publication to branches in the library repository. If external contributions must be supported, add a separate approval and staging design rather than using `pull_request_target` to execute untrusted code.

References:

- [Events that trigger workflows: `pull_request`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)
- [GitHub Actions contexts](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
- [Control workflow concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)

### Stable PR Snapshot Versus Commit-Specific Snapshot

The recommended initial format omits the commit hash:

```text
0.0.0-pr.417-SNAPSHOT
```

This version is intentionally mutable for the lifetime of the PR. It prevents every library commit from requiring a corresponding application POM change. Application CI must use Maven's update option when resolving it:

```bash
mvn -s ci/maven-settings.xml -U clean verify
```

If exact reproducibility during PR review becomes more important than convenience, change the format to:

```text
0.0.0-pr.417.4f92ac1-SNAPSHOT
```

That alternative requires the application PR to update its dependency after every library PR commit. Do not mix the two models without documenting which artifact an application test used.

## Link the Pull Requests

Use a machine-readable line in the application PR body:

```text
Depends-On: nggong/observation-protos#417
```

Also include a normal explanatory link for reviewers. The marker gives automation a stable way to identify the source library PR.

The library PR should link back to every known consumer PR. Initially, this can be a structured line maintained by the developer:

```text
Downstream-PR: nggong/scs-acquisition#892
```

Later, an application PR workflow can register this relationship automatically by posting a machine-readable comment on the library PR through the GitHub App.

Do not attempt to infer the relationship solely from branch names, commit messages, or whichever application PR happens to be open.

## Publish the Final Library Release

The release workflow shall:

1. Verify that the source library PR is merged.
2. Determine the required Semantic Version increment from the approved release metadata or PR label.
3. Validate the version against the latest release tag.
4. Run Protocol Buffer compatibility checks.
5. Create or verify the protected tag, such as `v2.4.0`.
6. Verify that the Maven version does not already exist.
7. Build and publish with `mvn -s ci/maven-settings.xml -Drevision=2.4.0 clean deploy`.
8. Create the immutable GitHub Release if GitHub Releases are part of the records model.
9. Send a release event to each registered consumer repository.

Recommended release labels are:

```text
release:patch
release:minor
release:major
```

The pipeline may calculate the next version from the latest tag and the approved label. Humans classify the change; automation calculates and validates the string.

For Protocol Buffer compatibility checking, consider [Buf breaking-change detection](https://buf.build/docs/breaking/). A Semantic Version increase identifies a break but does not replace a protocol migration plan.

## Send the Final Version to Consumer Repositories

After publishing the library, send a `repository_dispatch` event to each affected consumer repository. The payload should include enough information to validate and perform the update:

```json
{
  "event_type": "maven-library-released",
  "client_payload": {
    "coordinate": "org.nggong:observation-protos",
    "source_repository": "nggong/observation-protos",
    "source_pull_request": 417,
    "temporary_version": "0.0.0-pr.417-SNAPSHOT",
    "release_version": "2.4.0",
    "application_pull_request": 892,
    "property": "nggong.observation-protos.version"
  }
}
```

Reference:

- [Create a repository dispatch event](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)

The target application PR can come from the structured `Downstream-PR` registration described above. If a library has many consumers, keep an explicit consumer registry and send the release event to each consumer; each consumer can decide whether it has a matching open PR.

## Update the Application PR Automatically

The application repository listens for the release event:

```yaml
name: Finalize Maven dependency

on:
  repository_dispatch:
    types: [maven-library-released]

permissions:
  contents: write
  pull-requests: write
  packages: read

jobs:
  update:
    runs-on: ubuntu-latest
    env:
      GH_TOKEN: ${{ github.token }}
      MAVEN_USERNAME: ${{ github.actor }}
      # Requires package read access; otherwise use an authorized package-read secret.
      MAVEN_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    steps:
      - name: Check out trusted automation scripts
        uses: actions/checkout@v5
        with:
          # repository_dispatch identifies a revision on the default branch.
          ref: ${{ github.sha }}
          persist-credentials: false

      - name: Preserve trusted automation scripts
        # Keep the helpers outside the checkout so switching to the PR branch
        # cannot replace them. Include any supporting files the helpers need.
        run: cp -R ./ci "$RUNNER_TEMP/library-release-ci"

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: ${{ vars.JAVA_DISTRIBUTION }}
          java-version: ${{ vars.JAVA_VERSION }}

      - name: Validate dispatch payload
        # Read JSON from GITHUB_EVENT_PATH; reject missing or malformed fields.
        # Allowlist the source repository, coordinate, and dependency property.
        # Verify the release tag/package, open same-repository consumer PR,
        # and expected temporary property in that PR's POM using read APIs.
        # Fail closed; do not execute code from the PR or create a write token.
        run: bash "$RUNNER_TEMP/library-release-ci/validate-library-release-event.sh"

      - name: Create GitHub App token
        # Use actions/create-github-app-token as documented by GitHub.
        # This placeholder helper must obtain a short-lived installation token
        # scoped to this consumer repository, mask it, and export GH_TOKEN
        # through GITHUB_ENV for later steps. Configure Git authentication for
        # the App identity (for example, gh auth setup-git) and arrange token
        # revocation after the job. Prefer the action's token lifecycle support
        # when replacing this illustrative helper with a concrete workflow.
        run: bash "$RUNNER_TEMP/library-release-ci/create-automation-token.sh"

      - name: Check out the application PR branch
        env:
          APPLICATION_PR: ${{ github.event.client_payload.application_pull_request }}
        run: >
          gh pr checkout
          "$APPLICATION_PR"

      - name: Replace the temporary dependency
        # Use only the validated property/version. The final helper must also
        # verify the old value in the Git diff before committing the update.
        env:
          DEPENDENCY_PROPERTY: ${{ github.event.client_payload.property }}
          RELEASE_VERSION: ${{ github.event.client_payload.release_version }}
        run: >
          mvn
          -s "$RUNNER_TEMP/library-release-ci/maven-settings.xml"
          versions:set-property
          "-Dproperty=$DEPENDENCY_PROPERTY"
          "-DnewVersion=$RELEASE_VERSION"
          -DgenerateBackupPoms=false

      - name: Commit and push
        # Verify the diff changes only the allowlisted property in the intended
        # POM, from the expected temporary version to the validated release.
        # Commit as the App identity and push to the validated PR head branch.
        # Use a normal push; if the branch advanced, fail without force-pushing
        # and report the conflict on the PR. Do not stage unrelated changes.
        run: bash "$RUNNER_TEMP/library-release-ci/commit-final-library-version.sh"
```

The updater's `./ci/*` helpers are illustrative implementation boundaries, not scripts supplied by this documentation
repository.
Maven settings are committed configuration; the trusted copy above also retains `ci/maven-settings.xml`.
Token creation should use the standard GitHub App action rather than implementing authentication from scratch.
Payload validation and the guarded commit/push helper require more care: they must check remote release and PR state,
restrict the exact permitted edit, and handle failures or concurrent branch changes without overwriting developer work.
The trusted copies must not source scripts from the PR checkout.
Implementations shall report validation or update failures on the application PR when its identity can be safely established.

The scripts represented above must verify at least the following before writing:

- the event names an approved library repository and Maven coordinate;
- the release tag exists and identifies the published version;
- the package exists in the configured Maven repository;
- the application PR is open;
- the PR head branch belongs to the application repository rather than an untrusted fork;
- the current property still contains the expected temporary version; and
- the final version is not a snapshot or PR version.

The updater shall refuse to overwrite an unrelated dependency change. It shall comment on the application PR when validation fails.

## Use a GitHub App for Cross-Repository Automation

Create a GitHub App installed only on participating repositories. Grant the minimum repository permissions required to:

- read pull requests and repository metadata;
- send repository-dispatch events;
- update branches owned by the organization; and
- comment on pull requests when automation fails.

Use short-lived installation tokens. Store the App private key as an organization or repository secret and the App ID or client ID as a configuration variable.

References:

- [Making authenticated API requests with a GitHub App in a GitHub Actions workflow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)
- [Authenticating with a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)
- [GitHub Actions `GITHUB_TOKEN`](https://docs.github.com/en/actions/concepts/security/github_token)

Do not rely on a normal repository `GITHUB_TOKEN` to push the final application commit and start ordinary CI. Events caused by `GITHUB_TOKEN` are normally suppressed to prevent recursive workflow execution. Either push with the GitHub App identity or explicitly dispatch the verification workflow.

## Prevent Temporary Dependencies from Merging

Automatic updates are not sufficient enforcement. Add a required application check that rejects:

- direct dependencies ending in `-SNAPSHOT`;
- transitive dependencies ending in `-SNAPSHOT`; and
- any project-specific temporary form such as `0.0.0-pr.*`.

The Maven Enforcer Plugin provides the [`requireReleaseDeps`](https://maven.apache.org/enforcer/enforcer-rules/requireReleaseDeps.html) rule. Configure a merge-gate profile or dedicated workflow so normal PR integration tests may use the temporary dependency but the merge gate remains failed.

Expected check states before final publication:

```text
integration-tests       PASS
release-dependencies    FAIL
```

Expected states after the updater commits the final version:

```text
integration-tests       PASS
release-dependencies    PASS
```

Configure the application repository ruleset so both checks are required before merging to `main`.

Also configure the application container and SCS release-manifest pipelines to reject snapshot dependencies. This prevents a temporary dependency from reaching a candidate image even if a repository rule is bypassed.

## Cleanup

A scheduled cleanup workflow may delete temporary Maven artifacts when:

- the source library PR is closed;
- no open consumer PR declares `Depends-On` for that source PR;
- the configured grace period has expired; and
- no retained test record requires the artifact.

Final Semantic Version releases shall remain immutable. Cleanup shall never infer that a final version is unused solely because the current application no longer references it.

## Suggested Implementation Order

1. Add Maven CI-friendly versioning and committed settings; verify `mvn -s ci/maven-settings.xml install` locally.
2. Publish PR-specific snapshots from same-repository branches.
3. Add linked library and application PR conventions.
4. Add the required `release-dependencies` merge check.
5. Automate final Semantic Version publication.
6. Create the GitHub App and cross-repository dispatch.
7. Automate the application PR update.
8. Add temporary-artifact cleanup only after reference tracking is reliable.

Do not start with cleanup. An orphaned snapshot wastes storage; deleting an artifact still referenced by an open integration PR wastes developer time and weakens traceability.
