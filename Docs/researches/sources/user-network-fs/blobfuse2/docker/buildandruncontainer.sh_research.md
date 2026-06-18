## sources/user-network-fs/blobfuse2/docker/buildandruncontainer.sh

Purpose: Convenience script that builds the blobfuse2 Docker image and runs it interactively when the image appears.

Important flow: Reads the blobfuse2 version from `../blobfuse2 --version`, derives tag `azure-blobfuse2.$ver`, calls `./buildcontainer.sh Dockerfile x86_64`, checks `docker images` for the tag, and runs `docker run -it --rm` with `SYS_ADMIN`, `/dev/fuse`, apparmor unconfined, and Azure storage environment variables. It documents `fuse` and `unfuse` commands inside the container.

State and dependencies: Depends on a built `../blobfuse2`, Docker, environment credentials, and the build script. It creates/runs a privileged container but does not persist container state due to `--rm`.

Risks: Tag format differs from `buildcontainer.sh` (`azure-blobfuse2-$2.$ver`), so the image lookup may fail. Uses unquoted variables and broad privileges. No tests; validation is manual via build/run success.
