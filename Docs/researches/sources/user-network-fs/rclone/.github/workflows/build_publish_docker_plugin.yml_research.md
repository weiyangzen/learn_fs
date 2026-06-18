# sources/user-network-fs/rclone/.github/workflows/build_publish_docker_plugin.yml

Purpose: Builds and publishes rclone Docker volume plugin images for release tags or manual runs.

Important APIs/types/functions: Workflow `Release Build for Docker Plugin` triggers on published releases and manual dispatch. Job `build_docker_volume_plugin` frees disk, checks out repository, logs into Docker Hub, loops over plugin architectures amd64/arm64/arm/v7/arm/v6, and invokes `make docker-plugin` with architecture-derived tags and release-version tags, plus latest/version tags for amd64.

Control flow: Release tag is parsed from `GITHUB_REF`. Each architecture build uses Makefile plugin targets to create and push Docker plugin artifacts.

State and persistence: Publishes Docker plugin images under `rclone/docker-volume-rclone` tags and creates temporary build directories handled by Makefile targets.

Dependencies and integration points: Depends on Docker, Makefile `docker-plugin`, Docker Hub credentials, and contrib plugin build context.

Risks: Docker plugin build/push requires privileged or compatible Docker environment. Secret names differ from image workflow (`DOCKER_HUB_USER`/`DOCKER_HUB_PASSWORD`). Partial architecture push failures can leave inconsistent tag sets.

Test signals: No explicit runtime smoke test; successful `make docker-plugin` and push are the only workflow signals.
