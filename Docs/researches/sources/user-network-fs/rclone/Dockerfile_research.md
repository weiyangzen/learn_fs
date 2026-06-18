# sources/user-network-fs/rclone/Dockerfile

Purpose: Multi-stage Docker build for the rclone container image.

Important APIs/types/functions: Builder stage uses `golang:alpine`, optional `ARG CGO_ENABLED=0`, installs make/bash/gawk/git, copies `go.mod`/`go.sum`, downloads and verifies modules, copies source, builds with `make`, and runs `./rclone version`. Final stage uses `alpine:latest`, installs ca-certificates/fuse3/tzdata, enables `user_allow_other`, copies rclone binary to `/usr/local/bin`, creates `rclone` user/group id 1009, sets `ENTRYPOINT ["rclone"]`, `WORKDIR /data`, and `XDG_CONFIG_HOME=/config`.

Control flow: Docker build caches module download before full source copy. BuildKit cache mount stores Go build cache. Final image contains only runtime dependencies and the compiled binary.

State and persistence: Image layers persist module/build dependencies in builder layers and runtime binary/config defaults in final image. Runtime config is expected under `/config`.

Dependencies and integration points: Used by Docker image workflow and Makefile indirectly. Depends on Alpine packages, Go modules, and Makefile build target.

Risks: `alpine:latest` is moving and can change runtime behavior. FUSE use inside containers requires host capabilities/devices. `CGO_ENABLED=0` default may differ from builds requiring mount/cmount features.

Test signals: Docker image workflow runs `rclone version` during build and after final multi-platform manifest creation.
