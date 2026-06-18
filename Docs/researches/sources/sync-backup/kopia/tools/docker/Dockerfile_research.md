<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/Dockerfile -->
# sources/sync-backup/kopia/tools/docker/Dockerfile

This Dockerfile builds the runtime Kopia image from `ubuntu:jammy`. It sets noninteractive locale/env defaults, Kopia config/log/cache/rclone paths, persistence behavior, and installs runtime packages before copying architecture-specific Kopia/rclone binaries based on `TARGETARCH`.

Control flow is Docker build-stage shell execution: install dependencies, create app directories, add binaries from `bin-amd64` or `bin-arm64`, expose volumes/ports as configured by the image, and define the Kopia server/client entrypoint behavior.

State is container filesystem layout under `/app` and environment defaults. Dependencies are Ubuntu package repositories, buildx `TARGETARCH`, and release script-provided binaries. Risks include base image CVEs, package drift, architecture copy mismatches, privileged/mount expectations, and env defaults affecting user deployments. Signals are Docker build/publish pipeline and compose smoke usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/Dockerfile -->
