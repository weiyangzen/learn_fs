<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service -->
# sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service

## Purpose

This systemd service runs rclone as a Docker volume plugin outside the managed plugin packaging flow.

## Important APIs, Types, and Functions

The unit requires Docker and the matching socket, orders itself before Docker startup, prepares volume/plugin config/cache directories, sets `RCLONE_CONFIG`, `RCLONE_CACHE_DIR`, and verbosity, and runs `/usr/bin/rclone serve docker`.

## Control Flow

systemd socket activation creates `/run/docker/plugins/rclone.sock`; the service starts before Docker so Docker can discover the volume plugin endpoint.

## State and Persistence Behavior

Persistent config and cache live under `/var/lib/docker-plugins/rclone`; volumes are under `/var/lib/docker-volumes/rclone`.

## Dependencies and Integration Points

It integrates systemd, Docker startup ordering, rclone's Docker volume server, and host filesystem directories.

## Risks and Test Signals

Risks include service ordering loops, missing FUSE permissions, stale sockets, and absent rclone binary. Tests should verify `systemctl start`, socket creation, Docker volume operations, restart behavior, and log output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service -->
