<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml -->
# sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml

## Purpose

This compose example runs `rclone serve webdav` in a container against `remote:/`.

## Important APIs, Types, and Functions

It defines `rclone-webdav-server`, uses `rclone/rclone`, enables verbose read-only WebDAV serving, documents optional address/port mappings, uses host networking by default, and mounts the host rclone config read-only.

## Control Flow

Compose starts rclone in serve-webdav mode; with host networking, the default loopback bind remains accessible on the host. Users can uncomment `--addr 0.0.0.0:8080` and port mapping for bridge networking.

## State and Persistence Behavior

The example serves data read-only and persists no container data. Host config is mounted read-only.

## Dependencies and Integration Points

It integrates Docker Compose, rclone serve webdav, host network or port mapping, and host-configured remotes.

## Risks and Test Signals

Risks include accidental network exposure if binding to `0.0.0.0`, missing local path mounts, and legacy compose syntax. Tests should validate compose syntax, confirm WebDAV listing/read, and verify read-only write rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml -->
