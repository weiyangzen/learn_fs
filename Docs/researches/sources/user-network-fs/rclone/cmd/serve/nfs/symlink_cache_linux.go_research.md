# sources/user-network-fs/rclone/cmd/serve/nfs/symlink_cache_linux.go

## Purpose

This Linux-only file upgrades the disk NFS handle cache to a symlink-backed cache using kernel file handles for faster lookup.

## Important APIs, Types, and Functions

`makeSymlinkCache` self-tests symlink write/read and installs symlink methods. Helpers include `addLengthPrefix`, `removeLengthPrefix`, `symlinkCacheWrite`, `symlinkCacheRead`, `symlinkCacheRemove`, and `symlinkCacheSuffix`. Constants `emptyPath` and `emptyPathBytes` represent empty symlink targets.

## Control Flow

Writing creates a symlink at the cache path pointing to the full VFS path, obtains the symlink's kernel file handle with `NameToHandleAt`, prefixes its length, and returns that as the NFS handle. Reading removes the prefix, opens by handle with `OpenByHandleAt`, reads the symlink target with `Readlinkat`, and restores empty-path substitution. Removal reads the target, rehashes it, and deletes the real cache symlink.

## State and Persistence Behavior

Cache entries are symlinks on disk. Handles depend on filesystem-native file handles, so backup/restore can break mappings. `handleType` is stored in the `diskHandler`.

## Dependencies and Integration Points

It depends on Linux `name_to_handle_at`, `open_by_handle_at`, `CAP_DAC_READ_SEARCH`, symlink semantics, and the disk handler hooks.

## Risks and Test Signals

Risks include permission failures, handle invalidation after filesystem restore, symlink target truncation at 1024 bytes, file-handle length validation, and close-error handling in the deferred close block. Cache tests exercise this backend when capabilities are available and skip with explicit errors otherwise.
