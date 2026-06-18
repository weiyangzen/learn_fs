# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.h

This header declares the DFS referral cache API and target-list iterator types.

Main contents:
- Exports `dfscache_wq` and `dfs_cache_ttl`.
- Defines `struct dfs_cache_tgt_list`, which owns a list of copied target iterators and a count.
- Defines `struct dfs_cache_tgt_iterator`, containing target name, path-consumed value, and list node.
- Provides initializer macros `DFS_CACHE_TGT_LIST_INIT` and `DFS_CACHE_TGT_LIST`.

Public API:
- Cache lifecycle: `dfs_cache_init()`, `dfs_cache_destroy()`.
- Lookup/refresh: `dfs_cache_find()`, `dfs_cache_noreq_find()`.
- Target hint and referral extraction: `dfs_cache_noreq_update_tgthint()`, `dfs_cache_get_tgt_referral()`.
- Target parsing: `dfs_cache_get_tgt_share()`.
- Path canonicalization: `dfs_cache_canonical_path()`.
- Remount and background refresh: `dfs_cache_remount_fs()`, `dfs_cache_refresh()`.

Inline helpers:
- `dfs_cache_get_tgt_iterator()` returns the first target iterator.
- `dfs_cache_get_next_tgt()` advances to the next target.
- `dfs_cache_free_tgts()` frees a copied target list.
- `dfs_cache_get_tgt_name()` returns an iterator’s name.
- `dfs_cache_get_nr_tgts()` returns target count.
- `dfs_cache_get_ttl()` returns the current refresh TTL.

Research notes:
- Callers receive owned target-list copies, not direct cache internals.
- The iterator order places the target hint first when available.
