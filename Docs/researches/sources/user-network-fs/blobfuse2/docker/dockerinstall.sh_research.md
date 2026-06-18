## sources/user-network-fs/blobfuse2/docker/dockerinstall.sh

Purpose: Host setup helper to remove Docker Desktop remnants, install Docker Engine on Ubuntu, adjust permissions, prune old images, and start Docker.

Important flow: Removes/purges Docker Desktop, updates apt, installs certificates and prerequisites, creates Docker apt keyring/source, installs Docker CE packages, creates `docker` group, adds current user, adjusts docker socket and `~/.docker` ownership/permissions, removes blobfuse images, prunes Docker system, starts service, and lists images/containers.

State and dependencies: Mutates system packages, apt sources, user groups, docker socket permissions, images, and service state. Requires sudo and network access to Docker repositories.

Risks: Highly privileged and destructive for Docker state. Backtick `docker rmi` can fail or remove unintended images if grep/cut output is broad. Group membership changes may require re-login. No `set -e`, so partial installs are possible. No automated tests; validation is command output.
