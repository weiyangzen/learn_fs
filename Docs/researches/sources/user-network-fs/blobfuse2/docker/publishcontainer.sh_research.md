## sources/user-network-fs/blobfuse2/docker/publishcontainer.sh

Purpose: Tags and pushes a built blobfuse2 Docker image to `blobfuse2containers.azurecr.io`.

Important flow: Reads blobfuse version, builds image name `azure-blobfuse2-$3.$ver`, logs into Azure Container Registry with username `$1` and password `$2`, tags local `$image:latest` to the registry path, pushes it, and logs out.

State and dependencies: Mutates Docker local tags and remote registry state. Depends on a previously built image, Docker CLI, network, and valid ACR credentials.

Risks: Password is passed on the command line and can be visible in process history. No `set -e`, so push/tag errors can be missed. Image naming must match build script output. No tests; success is registry push completion.
