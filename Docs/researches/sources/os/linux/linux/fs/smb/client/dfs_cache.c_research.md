# File Research: sources/os/linux/linux/fs/smb/client/dfs_cache.c

## Purpose
Implements the in-kernel DFS referral cache for CIFS/SMB: canonical path handling, referral lookup/fetch/update, target iteration copies, `/proc` inspection and flushing, TTL scheduling, remount refresh, and background refresh work.

## Main Interfaces
- Cache lifecycle: `dfs_cache_init()`, `dfs_cache_destroy()`.
- Lookup APIs: `dfs_cache_find()`, `dfs_cache_noreq_find()`.
- Target APIs: `dfs_cache_get_tgt_referral()`, `dfs_cache_get_tgt_share()`, `dfs_cache_noreq_update_tgthint()`.
- Path normalization: `dfs_cache_canonical_path()`.
- Refresh/remount: `dfs_cache_remount_fs()`, `dfs_cache_refresh()`.
- `/proc` operations: `dfscache_proc_ops`.

## Data Model
`struct cache_entry` stores a canonical DFS path, referral header flags, TTL, expiration time, server type, referral flags, path-consumed length, a target list, target count, and a target hint. `struct cache_dfs_tgt` stores one referral target name and its path-consumed value.

The cache is a 512-bucket hash table with a maximum of 1024 entries. Hashing and equality are case-insensitive using the cache codepage, normally UTF-8.

## Control Flow
`dfs_cache_find()` canonicalizes the caller’s path, then calls `cache_refresh_path()`. If an entry is present and fresh, it is returned under the read lock. If missing, expired, or force-refreshed, the code drops the cache lock, issues `get_dfs_refer()` over IPC, then reacquires the write lock to add or update the entry.

`lookup_cache_entry()` supports exact matching and longest component-prefix matching for link referral behavior. On success, callers can copy a single referral via `setup_referral()` and/or copy all targets into an external `dfs_cache_tgt_list`.

Background refresh walks DFS sessions attached to a tcon, refreshes their referral paths, refreshes the tcon referral, and requeues itself using the global minimum cache TTL.

## State And Synchronization
- Uses `htable_rw_lock` to protect hash table entries and target lists.
- Uses `READ_ONCE`/`WRITE_ONCE` for target-hint access.
- Uses `atomic_t cache_count` and `atomic_t dfs_cache_ttl`.
- Drops the cache lock before network referral requests to avoid reconnect/cache deadlocks.
- Uses `dfscache_wq` for delayed refresh work.

## Integration Points
- Calls dialect `get_dfs_refer()` through `ses->server->ops`.
- Uses `dns_resolve_unc()` to compare target share hosts with active TCP server addresses.
- Uses `cifs_signal_cifsd_for_reconnect()` when forced refresh shows the current tcon should move to a different DFS target.
- Uses `cifs_setup_ipc()` to ensure referral refresh has an IPC tcon.
- Uses `cifs_autodisable_serverino()` and prefix-path flags during DFS remount.

## Notable Behaviors
- TTL is clamped to at least 120 seconds, and global refresh TTL tracks the minimum observed entry TTL.
- When the cache reaches its size limit, it purges single-target referrals first, then the oldest remaining entry.
- Target hints are preserved across referral updates where possible and moved to the front of copied target lists.
- `/proc/fs/cifs/dfscache` write accepts only `0` to flush the cache.
- `dfs_cache_get_tgt_share()` merges target prefix paths with the remaining DFS referral path.

## Risks And Review Focus
- Cache entries store `refs[0].path_name` by ownership transfer; referral cleanup must not double-free it.
- Lock release around referral fetch is necessary but introduces races handled by rechecking under write lock.
- Prefix matching must stay component-aware to avoid matching partial path components.
- Target hint updates assume the cached target still exists; missing checks here could dereference unexpected state if changed carelessly.
- Refresh paths can trigger reconnects, so lock ordering with session/tcon reconnect code is important.
