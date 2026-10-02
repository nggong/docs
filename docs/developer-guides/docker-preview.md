# Install Docker for Documentation Preview

The local documentation preview runs in Docker.
Use Docker's [official Ubuntu installation instructions] for the current prerequisites and installation procedure.
This guide adds only the steps needed to run the ngGONG documentation preview.

## Ubuntu

1. Install Make:

   ```sh
   sudo apt update
   sudo apt install make
   ```

2. Install Docker Engine by following the [official Ubuntu installation instructions].
   Use the installation method based on Docker's `apt` repository and complete Docker's verification step.

3. Follow Docker's [Linux post-installation instructions] to let your user run Docker commands without `sudo`.
   Review the security warning about membership in the `docker` group before you make this change.

4. Sign out and sign in again so that the new group membership takes effect.

5. Verify that Docker runs without `sudo`:

   ```sh
   docker run --rm hello-world
   ```

### Linux Mint

The Ubuntu procedure might work on Ubuntu-based Linux Mint releases, but Docker does not officially support Ubuntu
derivatives such as Linux Mint.
Use these instructions on Linux Mint only after you confirm that the release is compatible with its Ubuntu base.

## macOS

TBD: A developer familiar with the ngGONG macOS development environment must provide and verify this procedure.

## Start the Preview

From the root directory of this repository, start the preview server:

```sh
make preview
```

The first run builds the documentation image and can take several minutes.
When the preview server is ready, open <http://localhost:4848/>.
Press `Ctrl+C` in the terminal to stop the server.

[official Ubuntu installation instructions]: https://docs.docker.com/engine/install/ubuntu/
[Linux post-installation instructions]: https://docs.docker.com/engine/install/linux-postinstall/
