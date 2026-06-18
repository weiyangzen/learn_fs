# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.c

This file implements the CIFS DFS referral cache. It canonicalizes DFS paths, stores referral metadata and target lists, maintains target hints, exposes a procfs cache view/flush interface, refreshes expired referrals, and can force reconnects when refreshed targets no longer match an active DFS tcon.

Main data structures:
- `struct cache_entry`: hash-table entry keyed by canonical DFS path, with referral flags, TTL, expiry time, server type, path-consumed value, target count/list, and current target hint.
- `struct cache_dfs_tgt`: cached target node name and path-consumed value.
- Global cache state: 512-bucket hlist table, max 1024 entries, `htable_rw_lock`, slab cache, `dfscache_wq`, `dfs_cache_ttl`, cache codepage, and entry count.

Main responsibilities:
- Initialize/destroy DFS cache resources with `dfs_cache_init()` and `dfs_cache_destroy()`.
- Canonicalize paths into the cache codepage using `dfs_cache_canonical_path()`.
- Hash and compare paths case-insensitively using the cache NLS table.
- Lookup referrals by exact path or whole-component prefix for longer referral requests.
- Refresh missing, expired, or forced cache entries by issuing `get_dfs_refer` through an IPC session.
- Copy referral data into cache entries while preserving target hint ordering where possible.
- Return either a single `dfs_info3_param` referral or a complete `dfs_cache_tgt_list`.
- Update target hints without network I/O through `dfs_cache_noreq_update_tgthint()`.
- Parse target shares and merged prefix paths with `dfs_cache_get_tgt_share()`.
- Periodically refresh DFS sessions and tcon referrals through `dfs_cache_refresh()`.
- On forced remount refresh, mark the SMB connection for reconnect if the active target is no longer present.

Important flows:
- `dfs_cache_find()` canonicalizes the path, refreshes if necessary, then returns referral and/or target list data.
- `cache_refresh_path()` first looks under read lock, drops locks before network I/O, then reacquires write lock to add or update the entry.
- `dfs_cache_noreq_find()` reads an existing cache entry only and never sends referral requests.
- `refresh_tcon_referral()` checks whether the cached referral is missing/expired/forced, validates the root IPC session, fetches new refs, updates cache, and optionally reconnects.
- `dfs_cache_remount_fs()` force-refreshes a DFS mount, disables serverino assumptions, forces prefix-path use, and lets refresh logic decide whether reconnect is needed.

Concurrency and lifetime:
- `htable_rw_lock` protects cache table and entries.
- Network referral requests are performed outside the cache lock to avoid deadlocks with reconnect paths.
- Target hints are read/written with `READ_ONCE()`/`WRITE_ONCE()`.
- Target lists returned to callers are deep copies and must be freed by `dfs_cache_free_tgts()`.
- Cache purge favors removing single-target referrals first, then the oldest entry if still over limit.

External dependencies:
- Uses dialect `get_dfs_refer` operation through `cifs_ses`.
- Uses DNS resolution for target-share IP matching.
- Calls reconnect signaling when refreshed DFS targets require failover.

Research notes:
- The cache uses a minimum referral TTL of 120 seconds and tracks a global refresh cadence as the minimum observed cache TTL capped by configured/default TTL.
- Prefix lookup implements DFS referral matching for paths below an existing root/link referral.
- Forced refresh is used by remount to detect target-list changes and trigger failover.
