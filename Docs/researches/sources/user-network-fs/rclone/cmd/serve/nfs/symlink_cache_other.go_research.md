# sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_other.go

## Purpose

This Unix non-Linux fallback reports that the symlink NFS handle cache is unsupported.

## Important APIs, Types, and Functions

`makeSymlinkCache` returns `ErrorSymlinkCacheNotSupported`.

## Control Flow

The disk handler remains unmodified, and cache selection fails for `--nfs-cache-type symlink` on non-Linux Unix systems.

## State and Persistence Behavior

No state is written.

## Dependencies and Integration Points

Build tags are `unix && !linux`. `Handler.getCache` surfaces this error, and tests skip symlink-cache cases when it appears.

## Risks and Test Signals

The fallback is clear and intentional. Cross-platform build and skip behavior in `cache_test.go` are the relevant signals.
