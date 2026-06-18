<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket -->
# sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket

## Purpose

This socket unit exposes the Docker plugin Unix socket for rclone's volume driver service.

## Important APIs, Types, and Functions

It listens on `/run/docker/plugins/rclone.sock` and is installable under `sockets.target`.

## Control Flow

systemd creates the socket before the service starts, allowing Docker to connect to the rclone volume driver endpoint.

## State and Persistence Behavior

The socket is runtime state under `/run`; it is not persistent across boots.

## Dependencies and Integration Points

It pairs with `docker-volume-rclone.service` and Docker's plugin discovery path.

## Risks and Test Signals

Risks include socket path mismatch, permissions, and stale runtime files. Tests should enable/start the socket and confirm Docker can reach the plugin endpoint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket -->
