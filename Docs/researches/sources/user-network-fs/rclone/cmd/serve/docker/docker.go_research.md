# sources/user-network-fs/rclone/cmd/serve/docker/docker.go

## Purpose

This file registers the `rclone serve docker` command and global plugin options.

## Important APIs, Types, and Functions

Global settings include `pluginName`, `pluginScope`, `baseDir`, socket/spec paths, `stateFile`, `socketAddr`, `socketGid`, `canPersist`, `forgetState`, and `noSpec`. `Command` is the Cobra command; `help` trims embedded `docker.md`.

## Control Flow

Command initialization adds Docker-specific, mount, and VFS flags. Runtime creates a `Driver`, wraps it in a `Server`, then serves on the default plugin Unix socket, an explicit Unix socket path, or a TCP address with optional spec-file writing.

## State and Persistence Behavior

Persistent state is handled by `Driver` in the rclone cache dir. Command globals configure where sockets, specs, and volume mountpoints live.

## Dependencies and Integration Points

It integrates Cobra, `serve.Command`, mountlib, VFS flags, embedded docs, and platform socket helpers.

## Risks and Test Signals

Global variables mean tests and repeated command setup must avoid cross-test contamination. Persisted remote creation is disabled by `canPersist=false`. API and option tests cover most driver behavior, but command-line flag combinations are not exhaustively tested.
