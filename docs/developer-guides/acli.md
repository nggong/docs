# Install and Use Atlassian CLI

The Atlassian command-line interface (CLI), `acli`, provides terminal access to Jira Cloud.
This guide covers installation on the primary ngGONG development platforms, initial authentication, and a few
read-only commands.

You must have an Atlassian account with access to the Jira site that you want to query.

## Install `acli`

### Debian-Based Linux

These steps apply to Ubuntu, KDE Neon, and other Debian-based distributions.
They configure Atlassian's Advanced Package Tool (APT) repository so that normal system updates can update `acli`.

1. Install the required tools:

   ```sh
   sudo apt-get install -y wget gnupg2
   ```

2. Add the Atlassian package-signing key and repository:

   ```sh
   sudo mkdir -p -m 755 /etc/apt/keyrings
   wget -nv -O- https://acli.atlassian.com/gpg/public-key.asc \
       | sudo gpg --dearmor -o /etc/apt/keyrings/acli-archive-keyring.gpg
   sudo chmod go+r /etc/apt/keyrings/acli-archive-keyring.gpg
   acli_architecture="$(dpkg --print-architecture)"
   echo "deb [arch=$acli_architecture signed-by=/etc/apt/keyrings/acli-archive-keyring.gpg]" \
       "https://acli.atlassian.com/linux/deb stable main" \
       | sudo tee /etc/apt/sources.list.d/acli.list > /dev/null
   ```

3. Install `acli`:

   ```sh
   sudo apt update
   sudo apt install -y acli
   ```

See Atlassian's [Linux installation guide] for binary installation without APT and for Red Hat-based distributions.

### macOS

Install `acli` with Homebrew:

```sh
brew tap atlassian/homebrew-acli
brew install acli
```

See Atlassian's [macOS installation guide] for manual binary installation.
Windows users must follow Atlassian's [Windows installation guide].

### Verify the Installation

Display the installed version:

```sh
acli --version
```

Atlassian supports each CLI release for six months.
Use the [official upgrade instructions] to keep the tool current.

## Authenticate with Jira Cloud

Browser-based OAuth authentication avoids putting an API token in a command or file and is preferred for interactive
developer use.

1. Start the login:

   ```sh
   acli jira auth login --web
   ```

2. In the browser, select the Jira site and approve access.
3. Return to the terminal and select the same site.
4. Confirm the active account and site:

   ```sh
   acli jira auth status
   ```

For environments where browser authentication is not available, follow Atlassian's [API token authentication
instructions].
Do not put an API token in a repository or expose it in shell history.

## Basic Jira Commands

Atlassian calls Jira tickets **work items** in `acli` commands.
Replace `KEY-123` in these examples with a Jira ticket key that you can access.

Display the ticket's standard fields, including its description:

```sh
acli jira workitem view KEY-123
```

Display only the summary and description:

```sh
acli jira workitem view KEY-123 --fields summary,description
```

Return the ticket as JSON for use in a script:

```sh
acli jira workitem view KEY-123 --json
```

Open the ticket in a browser:

```sh
acli jira workitem view KEY-123 --web
```

See the [`workitem view` command reference] for all supported fields and options.

## Get Help

Use command-specific help first:

```sh
acli jira workitem view --help
```

For authentication failures, command errors, or trace IDs, use Atlassian's [troubleshooting guide].

[Linux installation guide]: https://developer.atlassian.com/cloud/acli/guides/install-linux/
[macOS installation guide]: https://developer.atlassian.com/cloud/acli/guides/install-macos/
[Windows installation guide]: https://developer.atlassian.com/cloud/acli/guides/install-windows/
[official upgrade instructions]: https://developer.atlassian.com/cloud/acli/guides/update-install-guide/
[API token authentication instructions]:
  https://developer.atlassian.com/cloud/acli/guides/how-to-get-started/#authentication-using-api-token
[`workitem view` command reference]:
  https://developer.atlassian.com/cloud/acli/reference/commands/jira-workitem-view/
[troubleshooting guide]: https://developer.atlassian.com/cloud/acli/guides/troubleshooting-guide/
