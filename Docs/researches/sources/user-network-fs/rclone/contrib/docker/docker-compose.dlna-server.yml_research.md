<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml -->
# sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml

## Purpose

This compose example runs `rclone serve dlna` in a container against `remote:/`.

## Important APIs, Types, and Functions

It defines a single `rclone-dlna-server` service using `rclone/rclone`, passes command-line arguments for verbose DLNA serving, custom DLNA name, and read-only mode, uses host networking for broadcast discovery, and mounts the host rclone config read-only.

## Control Flow

Compose starts the container with host network access; rclone reads config from `/root/.config/rclone` and serves the selected remote via DLNA until stopped.

## State and Persistence Behavior

The example is read-only by default and stores no container state except logs. Host config is mounted read-only.

## Dependencies and Integration Points

It integrates Docker Compose, rclone serve dlna, host-network multicast/broadcast behavior, and host rclone remotes.

## Risks and Test Signals

Risks include old compose syntax, host-network portability, exposing media over the LAN, and missing local-volume mappings for remotes that reference local paths. Tests should run compose config validation and a DLNA discovery/client smoke test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml -->
