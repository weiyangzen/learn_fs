# sources/test-tools/stress-ng/.github/workflows/container-image-stable.yml

Purpose: release-triggered workflow that publishes stable stress-ng container images.

Important APIs and control flow: on published release, it lowercases the repository name, checks out code, configures QEMU/buildx, authenticates to GHCR and DockerHub, computes Docker metadata, prints limits, and pushes SHA and `latest` tags for four Linux architectures.

State and persistence: creates long-lived registry tags tied to release commits and also overwrites `latest`.

Dependencies and integration: depends on GitHub Packages write permission, DockerHub credentials, and `docker/build-push-action`.

Risks and test signals: release publication can overwrite `latest`; no vulnerability scan is included unlike edge workflow; action versions are older. Signals are successful multi-platform manifest creation and registry push.
