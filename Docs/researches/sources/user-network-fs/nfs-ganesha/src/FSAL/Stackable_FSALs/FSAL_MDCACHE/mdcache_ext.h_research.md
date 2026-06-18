# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_ext.h

## Purpose

This header exposes MDCACHE configuration and a small external helper for code outside the private MDCACHE implementation. It primarily defines `struct mdcache_parameter`, the global cache tuning structure. The source was read as a complete 178-line file.

## Important APIs, Types, and Functions

Important symbols are `MDCACHE_AVL_CHUNK_DEFAULT`, `struct mdcache_parameter`, `extern struct mdcache_parameter mdcache_param`, and `get_readdir_mode`. Parameters cover partition counts, cache sizes, directory invalidation, AVL chunking, entry/chunk high-water marks, LRU intervals, FD caching/reaper thresholds, dirmap limits, delegation scaling, and cached-owner override behavior.

## Control Flow

`get_readdir_mode` asks the active export for `fs_readdir_mode`. If the sub-FSAL returns `FSAL_RDDIR_CHUNK_USE_CONFIG`, it converts configuration and export options into either `FSAL_RDDIR_CHUNK_NEVER` or `FSAL_RDDIR_CHUNK_ALWAYS`.

## State and Persistence Behavior

`mdcache_param` is process-global configuration loaded elsewhere. It governs in-memory cache sizing, reaper behavior, FD caching, and directory chunking. It does not itself persist state.

## Dependencies and Integration Points

It includes `nfs_exports.h` and uses `op_ctx`, export ops, and export options. Many MDCACHE files consult these parameters to decide readdir, LRU, and FD behavior.

## Risks and Edge Cases

The header labels these external hooks as hacks to remove, so callers should not expand the public surface casually. `get_readdir_mode` depends on `op_ctx` and a valid active export. Misconfigured chunk sizes or FD thresholds can cause memory pressure or poor performance.

## Test Signals

Config parsing tests for every field, readdir mode tests for sub-FSAL return values plus `EXPORT_OPTION_NO_DIR_CACHING`, and stress tests around LRU/FD high-water behavior.
