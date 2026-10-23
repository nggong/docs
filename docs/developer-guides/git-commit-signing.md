# Set Up Git Commit Signing

This guide configures Git to sign commits with a Secure Shell (SSH) key.
It applies to current Debian-based Linux distributions and macOS.

## What This Setup Does

The setup:

- creates a dedicated SSH key for commit signing;
- enables automatic commit signing for all Git repositories; and
- selects the ngGONG identity and signing key for repositories under `~/nggong/`.

The signing key is directory-specific because a developer can use different identities and signing keys for work and
personal repositories.
The setting that enables automatic signing is global.

## Prerequisites

Install Git and OpenSSH before you continue.
SSH commit signing requires Git 2.34 or later.

Check the installed versions:

```sh
git --version
ssh -V
```

## Create a Signing Key

Create a dedicated Ed25519 key:

```sh
ssh-keygen -t ed25519 \
    -f "$HOME/.ssh/id_ed25519_nggong_signing" \
    -C "ngGONG Git commit signing"
```

Enter a strong passphrase when `ssh-keygen` prompts for one.
The command creates two files:

```text
~/.ssh/id_ed25519_nggong_signing       Private key
~/.ssh/id_ed25519_nggong_signing.pub   Public key
```

Keep the private key private.
Do not copy it to GitHub, share it, or add it to a repository.

A dedicated signing key limits the effect of replacing a key and keeps commit signing separate from SSH authentication.
Create a separate signing key on each computer instead of copying a private key between computers.

## Add the Public Key to GitHub

Display the public key:

```sh
cat "$HOME/.ssh/id_ed25519_nggong_signing.pub"
```

Copy the complete output, then:

1. Open your GitHub account settings.
2. Select **SSH and GPG keys**.
3. Select **New SSH key**.
4. Select **Signing Key** as the key type.
5. Enter a title that identifies the computer.
6. Paste the public key and add it.

If you use GitHub CLI, you can do the same operation with:

```sh
gh ssh-key add "$HOME/.ssh/id_ed25519_nggong_signing.pub" \
    --type signing \
    --title "ngGONG signing key"
```

Add the key to the GitHub account that you use for ngGONG work.
The key belongs to your account, not to the ngGONG organization.

## Configure the ngGONG Identity and Key

Create a separate Git configuration file for ngGONG repositories.
Replace the example name and email address with your own values:

```sh
git config --file "$HOME/.gitconfig-nggong" user.name "YOUR NAME"
git config --file "$HOME/.gitconfig-nggong" user.email "YOUR-EMAIL@example.org"
git config --file "$HOME/.gitconfig-nggong" \
    user.signingKey "$HOME/.ssh/id_ed25519_nggong_signing"
```

Use an email address associated with your GitHub account.

The last command records an absolute path to the private key.
Git can then request the key passphrase when it signs a commit; the key does not have to be loaded into `ssh-agent`.

## Apply the Configuration Under `~/nggong/`

Add a conditional include to your global Git configuration:

```sh
git config --global 'includeIf.gitdir:~/nggong/.path' "$HOME/.gitconfig-nggong"
```

The resulting portion of `~/.gitconfig` is equivalent to:

```ini
[includeIf "gitdir:~/nggong/"]
    path = /absolute/path/to/.gitconfig-nggong
```

The trailing slash in `gitdir:~/nggong/` is important.
It makes the condition apply recursively to Git repositories below that directory.

Enable SSH signing and automatic commit signing globally:

```sh
git config --global gpg.format ssh
git config --global commit.gpgSign true
```

These two settings apply to all repositories.
Repositories outside `~/nggong/` must provide a signing key through another conditional include, a global default, or
repository-local configuration.
Without a signing key, Git will fail instead of creating an unsigned commit.

## Verify the Effective Configuration

Run these commands from an ngGONG repository:

```sh
cd "$HOME/nggong/REPOSITORY"
git config --show-origin --get user.name
git config --show-origin --get user.email
git config --show-origin --get user.signingKey
git config --show-origin --get gpg.format
git config --show-origin --get commit.gpgSign
```

Confirm that:

- the name, email address, and signing key come from `.gitconfig-nggong`;
- the signing format is `ssh`; and
- automatic commit signing is `true`.

## Test Commit Signing

Create the test commit on a branch where an empty commit is acceptable:

```sh
git commit --allow-empty -m "Test SSH commit signing"
git log --show-signature -1
```

Git can report that no allowed-signers file is configured even when the commit contains a valid SSH signature.
An allowed-signers file is a separate local trust configuration and is not required for GitHub verification.

Push the test commit and inspect it on GitHub.
GitHub should mark it **Verified** when the signature matches the signing key registered with your account.

## Security and Maintenance

- Protect the private key with a passphrase.
- Never commit or share the private key.
- Upload only the `.pub` file to GitHub.
- Use a different signing key on each computer.
- Remove the public key from GitHub if its private key is lost or compromised.
- Replace the key if you suspect that another person obtained the private key or its passphrase.

## Repository-Specific Configuration

The directory-based configuration is preferred for repositories under `~/nggong/`.
If one repository must use a different identity or signing key, run the following commands in that repository:

```sh
git config --local user.name "YOUR NAME"
git config --local user.email "YOUR-EMAIL@example.org"
git config --local user.signingKey "$HOME/.ssh/OTHER_SIGNING_KEY"
git config --local gpg.format ssh
git config --local commit.gpgSign true
```

Repository-local settings are stored in `.git/config` and take precedence over global and conditionally included settings.
Use them only when the `~/nggong/` rule is not correct for that repository.

## References

- [Git conditional includes]
- [Git `user.signingKey` configuration]
- [GitHub: About commit signature verification]
- [GitHub: Add a new SSH key]
- [GitHub: Tell Git about an SSH signing key]

[Git conditional includes]: https://git-scm.com/docs/git-config#_conditional_includes
[Git `user.signingKey` configuration]:
  https://git-scm.com/docs/git-config#Documentation/git-config.txt-usersigningKey
[GitHub: About commit signature verification]:
  https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification
[GitHub: Add a new SSH key]:
  https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account
[GitHub: Tell Git about an SSH signing key]:
  https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key
