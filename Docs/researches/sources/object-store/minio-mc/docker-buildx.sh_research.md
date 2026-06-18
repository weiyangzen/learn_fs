## sources/object-store/minio-mc/docker-buildx.sh

Purpose: release helper for publishing multi-architecture mc Docker images to Docker Hub and Quay. It disables IPv6, derives the release tag from `git describe --abbrev=0 --tags`, builds/pushes standard and old-CPU images, prunes buildx cache between builds, then re-enables IPv6.

State changes include host sysctl IPv6 settings, remote pushed images, and Docker build cache pruning. Dependencies are bash, sudo, git tags, Docker buildx, Dockerfiles `Dockerfile.release` and `Dockerfile.release.old_cpu`, and registry credentials. Risks are significant because host networking is modified and images are pushed with `latest` tags; failures before the final sysctl can leave IPv6 disabled. Test signal is manual/release-pipeline execution, not unit tests.
