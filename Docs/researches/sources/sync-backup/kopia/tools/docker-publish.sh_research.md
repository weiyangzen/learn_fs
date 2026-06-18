<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker-publish.sh -->
# sources/sync-backup/kopia/tools/docker-publish.sh

This script prepares and publishes multi-architecture Kopia Docker images. It copies amd64 and arm64 release artifacts plus `rclone` into the Docker build directory, sets executable permissions, computes tags from release metadata, builds/pushes images, and cleans copied binaries afterward.

Control flow defaults `DIST_DIR` and `DOCKERHUB_REPO`, derives extra tags for stable/testing releases, and uses Docker build/push commands against `tools/docker`. It assumes specific distribution artifact layout names.

State is temporary copied binaries in `tools/docker/bin-*` and remote Docker registry tags. Dependencies are bash, Docker, dist artifact naming, and DockerHub credentials. Risks include stale binaries if cleanup fails, wrong tags on version parsing mistakes, overwriting `latest`, and lack of rollback on partial pushes. Signals are release pipeline runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker-publish.sh -->
