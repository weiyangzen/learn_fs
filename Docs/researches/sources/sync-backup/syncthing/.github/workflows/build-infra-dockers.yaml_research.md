# sources/sync-backup/syncthing/.github/workflows/build-infra-dockers.yaml

Purpose: GitHub Actions workflow that builds and publishes infrastructure service container images on `infrastructure` and `infra-*` branch pushes.

Important APIs/types/functions: single matrix job `docker-syncthing` builds `stcrashreceiver`, `strelaypoolsrv`, `stupgrades`, and `ursrv`. It sets Go 1.26, `CGO_ENABLED=0`, build metadata, logs into Docker Hub and GHCR, builds linux arm64/amd64 binaries with `go run build.go`, computes branch/sha/latest tags, and uses Docker Buildx with per-package `Dockerfile.<pkg>`.

Control flow: checkout with full history, setup Go, authenticate registries, build binaries for two architectures, set tags, then build/push multi-arch images. Latest tags are added only on the `infrastructure` branch; all branches get sha tags.

State and persistence behavior: no repo files are modified. Persistent outputs are registry images in Docker Hub and `ghcr.io/syncthing/infra`.

Dependencies/integration: relies on `build.go` targets for infrastructure binaries, package-specific Dockerfiles, Docker credentials, GHCR token, QEMU, and Buildx.

Risks/test signals: branch-limited latest tagging protects production-ish images but bad credentials or Dockerfile drift breaks publishing. Test signals are successful matrix jobs and presence of both arch manifests for each infrastructure image.
