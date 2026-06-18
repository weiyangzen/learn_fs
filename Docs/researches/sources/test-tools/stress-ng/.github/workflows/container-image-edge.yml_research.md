# sources/test-tools/stress-ng/.github/workflows/container-image-edge.yml

Purpose: builds and publishes multi-architecture edge container images on pushes to `master` and daily schedule, then scans the `latest` image.

Important APIs and control flow: the build job derives a lowercase image repository, checks out code, sets up QEMU/buildx, logs into GHCR and DockerHub, derives metadata, prints environment/limits, builds and pushes tags for SHA and `latest` across amd64, s390x, ppc64le, and arm64. The scan job runs Trivy and uploads SARIF.

State and persistence: publishes registry images and SARIF security scan results.

Dependencies and integration: uses Docker actions v2/v3/v4-era actions, GHCR package permissions, DockerHub secrets, Trivy, and CodeQL SARIF upload.

Risks and test signals: secrets are required for DockerHub; action versions are older; Trivy scans only GHCR `latest`; daily overwrite of `latest` means mutable deployment state. Signals are pushed image tags and uploaded SARIF.
