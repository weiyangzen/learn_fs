# sources/user-network-fs/rclone/cmd/serve/docker/unix_unsupported.go

## Purpose

This fallback reports that Docker plugin Unix sockets are unavailable on unsupported operating systems.

## Important APIs, Types, and Functions

`newUnixListener` returns nil listener, empty path, and the error `unix sockets require Linux or FreeBSD`.

## Control Flow

There is no filesystem or network action.

## State and Persistence Behavior

No state is persisted.

## Dependencies and Integration Points

Build tags are `!linux && !freebsd`. TCP mode can still be used by `ServeTCP`.

## Risks and Test Signals

The behavior is explicit and low-risk. Cross-platform build tests are the relevant signal.
