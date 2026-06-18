# sources/sync-backup/restic/docker/Dockerfile

## Purpose

This Dockerfile builds a restic container image. It uses a Go Alpine builder stage to compile restic from source and a minimal Alpine runtime stage with restic plus operational dependencies.

## Important APIs, Types, and Functions

- Builder stage: `FROM golang:1.26-alpine AS builder`, working directory `/go/src/github.com/restic/restic`, dependency cache via `COPY go.mod go.sum ./` and `go mod download`, source copy, and `go run build.go`.
- Runtime stage: `FROM alpine:latest AS restic`, installs `ca-certificates`, `fuse`, `openssh-client`, `tzdata`, and `jq`.
- Copies `/go/src/github.com/restic/restic/restic` to `/usr/bin`.
- Copies `docker/entrypoint.sh` to `/entrypoint.sh`.
- Defines `IONICE_CLASS`, `IONICE_PRIORITY`, and `NICE` environment defaults.
- Sets `ENTRYPOINT ["/entrypoint.sh"]`.

## Control Flow

Docker builds the binary in the first stage after downloading modules, then starts a fresh Alpine runtime image and copies only the resulting binary and entrypoint script. At container runtime, execution is delegated to `entrypoint.sh`, which wraps restic with optional `ionice` and `nice`.

## State and Persistence Behavior

Build cache state is managed by Docker layers, especially the separate module-download layer. The image itself contains the compiled restic binary and runtime packages. Runtime repository/cache persistence depends on user-mounted volumes and restic options, not the Dockerfile.

## Dependencies and Integration Points

It depends on Go, Alpine package repositories, `build.go`, module files, and `docker/entrypoint.sh`. Runtime packages support TLS certificates, FUSE-based mount usage, SSH backends, timezone handling, and JSON processing via `jq`. `docker/build.sh` is the local wrapper for building this Dockerfile.

## Risks and Edge Cases

- `golang:1.26-alpine` and `alpine:latest` are moving tags; reproducibility and compatibility depend on current image contents.
- `COPY . .` invalidates the build layer when any source changes.
- Runtime `fuse` support also requires container privileges/devices from the user.
- Entry point defaults intentionally avoid `ionice -c0 -n...` because BusyBox rejects that combination.

## Test Signals

Successful `docker/build.sh` or `docker build -f docker/Dockerfile` validates the build. Runtime smoke tests should run `restic version`, backend operations with mounted volumes, and optional `IONICE_CLASS`/`NICE` behavior.
