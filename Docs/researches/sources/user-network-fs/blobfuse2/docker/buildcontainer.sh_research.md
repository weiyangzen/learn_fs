## sources/user-network-fs/blobfuse2/docker/buildcontainer.sh

Purpose: Builds a blobfuse2 Docker image from the repository source and local Dockerfile context.

Important flow: Moves to repo root, runs `./build.sh`, lists the generated binary, returns to docker directory, copies the binary plus rsyslog/logrotate files into the Docker build context, computes version and tag `azure-blobfuse2-$2.$ver`, removes any existing image, runs `sudo docker build -t $tag -f $1 .`, lists images, removes copied build-context artifacts, and prints matching image status.

State and dependencies: Mutates the docker directory temporarily with copied binary/config files and mutates local Docker image cache. Depends on `build.sh`, Docker daemon, sudo, and setup files.

Risks: No `set -e`, so failed commands can cascade. Unquoted args and variables can break. Image removal is unconditional for the computed tag. Cleanup removes known copied files only. Test signal is manual image listing and downstream run script.
