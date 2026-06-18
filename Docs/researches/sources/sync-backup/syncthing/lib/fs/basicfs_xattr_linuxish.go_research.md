# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_linuxish.go

## Purpose
Lists extended attribute names on Linux and Darwin using NUL-separated `Llistxattr` results.

## Important APIs, Types, and Functions
`listXattr(path string) ([]string, error)` uses `unix.Llistxattr`, grows the buffer on `ERANGE`, compacts empty NUL split parts, sorts names, and returns them.

## Control Flow
Initial 1024-byte read is retried with exact size when too small. Errors wrap the path for diagnostics. Empty entries from trailing NULs are removed by `compact`.

## State and Persistence Behavior
Read-only metadata query.

## Dependencies and Integration Points
Used by `basicfs_xattr_unix.go` for xattr filtering and synchronization on Linux/Darwin.

## Risks
Darwin and Linux xattr naming and namespaces differ, but this file returns raw names for higher-level filtering. Concurrent xattr changes between size query and read can still error.

## Test Signals
Indirectly covered by `TestXattr` where xattrs are supported.
