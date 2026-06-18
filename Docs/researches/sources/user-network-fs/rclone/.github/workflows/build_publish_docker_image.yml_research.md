# sources/user-network-fs/rclone/.github/workflows/build_publish_docker_image.yml

Purpose: Builds and publishes multi-platform rclone Docker images to GitHub Container Registry and Docker Hub-style tags via a digest-then-merge workflow.

Important APIs/types/functions: Workflow `Build & Push Docker Images` triggers on push and manual dispatch. `build-image` matrix covers linux/amd64, 386, arm64, arm/v7, and arm/v6. Steps free disk, checkout, derive repository/platform/cache names, extract Docker metadata, set up QEMU/buildx, use Go build cache injection, login to GHCR, build/push digest images, and upload digest artifacts. `merge-image` downloads digests, extracts metadata tags/annotations, logs into Docker Hub and GHCR, creates manifest list, inspects, and runs `rclone version`.

Control flow: Per-platform jobs push untagged digest images to GHCR. The merge job waits for all digests and assembles a final manifest with semver/ref/sha/beta tags and OCI labels/annotations.

State and persistence: Writes registry images, build cache layers, digest artifacts retained for one day, and final manifest tags.

Dependencies and integration points: Depends on Docker Buildx/QEMU, `Dockerfile`, Docker metadata action, cache-dance, GHCR permissions, Docker Hub secrets, and GitHub artifact actions.

Risks: Registry authentication, cache growth, QEMU emulation, and runner disk pressure are key failure modes. The workflow uses shell-generated quoted tag strings, so metadata content must remain shell-safe.

Test signals: Final `docker run --rm ... version` confirms the merged image starts and contains rclone.
