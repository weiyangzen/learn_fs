# sources/sync-backup/bup/dev/mksock

## Purpose
Creates a Unix-domain socket filesystem entry for metadata/save/restore tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, creates `socket.AF_UNIX`, `SOCK_STREAM`, and binds to `get_argvb()[1]`.

## Control Flow
No explicit usage validation; it binds a socket to the first argument and exits, leaving the socket path.

## State and Persistence Behavior
Creates a socket node in the filesystem.

## Dependencies and Integration Points
Supports tests that need special file types.

## Risks and Test Signals
Risks are missing arg, stale existing path, and platform Unix socket availability. Signal is a created socket path.
