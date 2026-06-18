# sources/user-network-fs/rclone/cmd/serve/docker/systemd.go

## Purpose

This Linux implementation exposes systemd socket activation files to the Docker plugin Unix listener code.

## Important APIs, Types, and Functions

`systemdActivationFiles` returns `activation.Files(false)` only when `util.IsRunningSystemd()` is true.

## Control Flow

The function checks for systemd at runtime and returns either activated file descriptors or nil.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `linux && !android`. It integrates with `newUnixListener`, allowing systemd to pre-create the plugin socket.

## Risks and Test Signals

Risks are incorrect environment detection and multiple activated sockets. `unix.go` handles the multiple-socket error path. No direct tests cover systemd activation.
