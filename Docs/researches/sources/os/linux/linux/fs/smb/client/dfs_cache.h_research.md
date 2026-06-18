# File Research: sources/os/linux/linux/fs/smb/client/dfs_cache.h

## Purpose
Declares the DFS cache public API, target-list structures, workqueue/TTL globals, and inline target-list utilities.

## Main Contents
- Exposes `dfscache_wq` and `dfs_cache_ttl`.
- Defines `DFS_CACHE_TGT_LIST_INIT()` and `DFS_CACHE_TGT_LIST()` stack helpers.
- Defines `struct dfs_cache_tgt_list` and `struct dfs_cache_tgt_iterator`.
- Declares cache lifecycle, lookup, target parsing, canonicalization, remount, refresh, and proc operation interfaces.
- Provides inline helpers to get the first/next target, free copied target lists, get target names, count targets, and read TTL.

## Integration Points
Used by `dfs.c`, `dfs.h`, `dfs_cache.c`, and DFS reconnect logic in `connect.c`. The target-list API intentionally copies cache data so callers can iterate without holding cache internals longer than needed.

## Risks And Review Focus
- `dfs_cache_free_tgts()` relies on `tl_numtgts` and list state being initialized correctly.
- Callers must treat `dfs_cache_tgt_iterator` names as owned by the copied target list and not by the cache.
- The TTL helper returns the global atomic value, which is a cache-wide scheduling hint rather than a per-entry TTL.
