# sources/sync-backup/restic/.github/workflows/docker.yml

Purpose: release/nightly workflow for building and publishing multi-architecture Docker images to GitHub Container Registry and generating SLSA provenance.

Control flow/state: triggers on `v*` tags and `master` pushes. The build job only runs in `restic/restic`, checks out code, logs into GHCR, generates Docker metadata, sets up QEMU and Buildx, removes `.git` for non-master release consistency, then builds and pushes `docker/Dockerfile.release` for linux/386, amd64, arm, and arm64. A dependent reusable SLSA job signs/provides provenance for the pushed digest.

Dependencies/integration: uses Docker official actions, GHCR permissions, `secrets.GITHUB_TOKEN`, and `slsa-framework/slsa-github-generator`. Outputs include image name and digest.

Risks/test signals: action versions are pinned by commit for build dependencies but SLSA workflow is version-tagged. Removing `.git` changes version embedding behavior for releases. Validation comes from successful image push and provenance generation.
