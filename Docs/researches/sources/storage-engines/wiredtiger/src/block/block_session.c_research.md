# sources/storage-engines/wiredtiger/src/block/block_session.c

## Purpose

`block_session.c` provides session-local caches for block-manager extent structures. It reduces allocation churn for `WT_EXT` and `WT_SIZE` objects used by extent lists, with cleanup hooks tied to the session's block-manager state.

## Important APIs, Types, and Functions

The main exported helpers are `__wti_block_ext_alloc`, `__wti_block_ext_free`, `__wti_block_size_alloc`, `__wti_block_size_free`, `__wti_block_ext_prealloc`, and `__wti_block_ext_discard`. Private helpers include `__block_ext_alloc`, `__block_ext_prealloc`, `__block_ext_discard`, `__block_size_alloc`, `__block_size_prealloc`, `__block_size_discard`, and `__block_manager_session_cleanup`.

`WT_BLOCK_MGR_SESSION` holds `ext_cache`, `ext_cache_cnt`, `sz_cache`, and `sz_cache_cnt`. `WT_EXT` allocations include variable space for two pointer arrays per skip-list depth.

## Control Flow

Allocations first try the session cache. Reused `WT_EXT` nodes have both offset and size skip-list links cleared for their depth. If no cache exists, allocation falls back to heap allocation with a randomly chosen skip-list depth. Preallocation lazily creates `session->block_manager`, installs `session->block_manager_cleanup`, and fills both caches to a requested minimum. Freeing returns objects to the cache when available, or directly frees them if no block-manager session cache exists.

Discard trims caches to a maximum or fully drains them during cleanup. Cleanup drains both caches and frees the `WT_BLOCK_MGR_SESSION`.

## State and Persistence Behavior

This file is purely in-memory. It persists no file content, but it materially affects checkpoint/allocation performance by retaining extent/list nodes across operations in a session. Cache counts are advisory and checked for consistency only on full discard.

## Dependencies and Integration Points

The extent allocator in `block_ext.c` calls these helpers for every `WT_EXT`/`WT_SIZE` insert/remove. Checkpoint and free paths preallocate a small number of entries before acquiring or while holding allocator locks, reducing failure windows during list mutation. The session cleanup hook integrates with the broader session lifecycle.

## Risks and Edge Cases

Cache-count drift is tolerated during normal operation but reported on full cleanup. Reused `WT_SIZE` nodes are not explicitly cleared in this file beyond being removed from the free list, so callers must initialize fields before insertion. `__wti_block_ext_discard` assumes `session->block_manager` exists; callers should only use it after preallocation or initialization. Failure during preallocation can leave a partially filled but valid cache.

## Test Signals

Unit-test shims expose allocation, preallocation, discard, and cleanup helpers. Runtime validation comes from memory diagnostics, cache count consistency on cleanup, and extent-list correctness under allocation-heavy checkpoint/free workloads.
