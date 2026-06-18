<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile -->
# sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile

## Purpose

This Dockerfile builds the managed Docker volume plugin image for rclone by copying the rclone binary from a base image into a small Alpine runtime.

## Important APIs, Types, and Functions

The build arg `BASE_IMAGE` defaults to `rclone/rclone:latest`. Runtime setup installs `ca-certificates`, `fuse3`, and `tzdata`, creates `/data/config`, `/data/cache`, and `/mnt`, enables `user_allow_other`, and sets rclone-related environment variables.

## Control Flow

The first stage exposes `/usr/local/bin/rclone`; the final Alpine stage copies it to `/usr/bin/rclone`, prepares FUSE/config/cache/mount paths, verifies `rclone version`, sets `/data` as workdir, and launches `rclone serve docker`.

## State and Persistence Behavior

Plugin state is expected in mounted `/data/config`, `/data/cache`, and propagated `/mnt`. The image itself contains only the binary and package/runtime configuration.

## Dependencies and Integration Points

It integrates with Docker managed plugin packaging, FUSE device access, rclone Docker volume serving, proxy environment variables, and the companion `config.json`.

## Risks and Test Signals

Risks include mutable `latest` base image drift, Alpine package changes, FUSE permission requirements, and proxy/config defaults. Tests should build with pinned base images, run `rclone version`, and exercise plugin mount/create/remove flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile -->
