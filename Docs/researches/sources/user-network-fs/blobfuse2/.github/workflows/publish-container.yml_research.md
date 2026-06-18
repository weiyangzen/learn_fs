# sources/user-network-fs/blobfuse2/.github/workflows/publish-container.yml

## Purpose
This workflow builds a Blobfuse2 container image and publishes it to GitHub Container Registry when release-like tags are pushed.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `actions/setup-go@v6`, `docker/setup-buildx-action@v4`, `docker/login-action@v4`, `docker/metadata-action@v6`, and `docker/build-push-action@v7`. It calls `./build.sh` and copies the built binary plus setup files into `docker/`.

## Control Flow
On tag pushes matching `v*` or `blobfuse2-*`, the job installs FUSE dependencies, builds Blobfuse2, prepares Docker context, logs into `ghcr.io` with `GITHUB_TOKEN`, computes semver/ref tags for both `v` and `blobfuse-` tag formats, builds and pushes the Docker image from `docker/Dockerfile`, then deletes temporary copied files from `docker/`.

## State and Persistence Behavior
Persistent output is the pushed GHCR package `ghcr.io/azure/blobfuse2` with generated tags and labels. Workspace mutations under `docker/` are cleaned at the end.

## Dependencies and Integration Points
It depends on Go module settings, the repository Dockerfile, setup files, FUSE apt packages, and package write permission to GHCR.

## Risks and Edge Cases
Metadata semver patterns assume tags parse correctly with `v` or `blobfuse-` prefixes. Cleanup runs only after a successful push step; failed jobs may leave copied files in the ephemeral workspace. It does not build multi-arch images.

## Test Signals
Signals include successful binary build, generated Docker metadata, pushed GHCR tags for release tags, and ability to pull `ghcr.io/azure/blobfuse2:<tag>`.
