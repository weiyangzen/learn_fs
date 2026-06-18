# sources/user-network-fs/samba/source3/smbd/dfree.c

## Purpose
`dfree.c` computes disk free-space information returned to SMB clients. It supports administrator-provided `dfree command`, VFS `disk_free`, quota clamping, max disk size normalization, broken-platform fallbacks, and optional per-path memcache caching.

## Important APIs, types, and functions
- `get_dfree_info()` is the public entry point. It returns free 1 KiB blocks and fills block size, free blocks, and total blocks.
- `sys_disk_free()` performs uncached computation by external command or VFS and quota APIs.
- `handle_dfree_command()` runs the configured external command with the path and parses `dsize dfree bsize` from the first output line.
- `disk_norm()` enforces `max disk size`.
- `flush_dfree_cache()` clears `DFREE_CACHE`.

## Control flow
If caching is disabled, `get_dfree_info()` calls `sys_disk_free()` directly. With caching enabled, it builds a full path from the connection path and FSP name, uses the parent directory for regular files to reduce cardinality, and looks up a `struct dfree_cached_info` in `smbd_memcache()`. Valid entries are keyed by path and expire by `conn->lastused`. On cache miss, `sys_disk_free()` tries the external command first, otherwise calls `SMB_VFS_DISK_FREE()`, folds in quota values with a common minimum block size, repairs implausibly small block sizes and zero disk sizes, normalizes max disk size, and returns free space as 1 KiB blocks.

## State and persistence behavior
No persistent state is written. The only stored state is process-local memcache entries and a static `dfree_broken` flag used to log the broken-dfree warning only once.

## Dependencies and integration points
It depends on loadparm settings (`dfree command`, cache time, max disk size), VFS disk-free hooks, quota helpers, full-path utilities, and Samba memcache. SMB query filesystem information paths consume its output.

## Risks and edge cases
- External command output is trusted enough to affect reported capacity; bad values fall back only by missing fields, not semantic validation.
- Cache keys depend on full path construction and `conn->lastused`; stale values can be visible until cache expiry.
- Quota and filesystem block-size conversion must avoid overflow and preserve minimum block size semantics.
- Returning `(uint64_t)-1` signals failure and is not cached.

## Test signals
Tests should cover external command parsing with 1/2/3 fields, VFS fallback failure, quota clamping, max disk size cap, regular-file parent keying, cache hit/expiry/flush, and broken zero-total fallback behavior.
