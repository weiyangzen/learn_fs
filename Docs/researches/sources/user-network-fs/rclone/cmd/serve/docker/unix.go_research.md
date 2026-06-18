# sources/user-network-fs/rclone/cmd/serve/docker/unix.go

## Purpose

This Unix-socket implementation creates or adopts the Docker plugin socket on Linux and FreeBSD.

## Important APIs, Types, and Functions

`newUnixListener(path string, gid int)` checks systemd activation, normalizes socket paths, creates parent directories, removes stale sockets, listens on Unix domain sockets, chmods to `0660`, and chowns to root plus the requested group when running as root.

## Control Flow

If systemd provides exactly one socket, it returns a `net.FileListener` and no cleanup path. If more than one socket is provided, it errors. Otherwise it creates a socket under `/run/docker/plugins` for relative names and returns the created path for later cleanup.

## State and Persistence Behavior

It creates a socket filesystem entry and may delete a stale one. Cleanup is registered by `serve.go`.

## Dependencies and Integration Points

It depends on `systemdActivationFiles`, `file.MkdirAll`, platform Unix sockets, and Docker's plugin socket discovery convention.

## Risks and Test Signals

Risks include removing a stale path that belongs to another process, permissions/group mismatch preventing Docker access, and systemd listener type assumptions. Unix API tests exercise explicit socket creation on Linux when not skipped.
