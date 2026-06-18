# sources/user-network-fs/rclone/cmd/serve/docker/systemd_unsupported.go

## Purpose

This fallback keeps Docker plugin code buildable where systemd activation is not supported.

## Important APIs, Types, and Functions

`systemdActivationFiles` returns nil.

## Control Flow

There is no branching or runtime action.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `!linux || android`. `newUnixListener` sees nil and creates its own socket.

## Risks and Test Signals

The behavior is intentionally minimal. Platform build coverage is the main signal.
