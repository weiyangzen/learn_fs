# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_up.c

## Purpose
`mdcache_up.c` implements MDCACHE's lower-FSAL upcall vector. It consumes cache-related invalidation, update, close, and try-release upcalls, and forwards lock/delegation/layout notifications to the upper layer after establishing the correct MDCACHE operation context.

## Important APIs, Types, and Functions
- `mdc_up_invalidate()` finds a cached entry by lower-FSAL handle key, clears requested trust flags, optionally closes cached file state, invalidates cached parent handles, and releases cached ACLs.
- `mdc_up_try_release()` removes an otherwise idle entry from the cache hash when only the sentinel reference remains.
- `mdc_up_update()` applies a safe subset of lower-FSAL attribute updates and invalidates directory content when directory attributes change.
- `mdc_up_invalidate_close()` schedules asynchronous invalidation with close semantics.
- `mdc_up_lock_grant()`, `mdc_up_lock_avail()`, `mdc_up_layoutrecall()`, and `mdc_up_delegrecall()` pass state notifications upward through `super_up_ops`.
- `mdcache_export_up_ops_init()` copies upper upcall ops, initializes readiness, then overrides cache-aware operations with MDCACHE handlers.

## Control Flow
Each cache-affecting upcall takes a reference to the Ganesha export and creates a simple `op_ctx` for the MDCACHE export before touching cache state. Invalidation hashes the lower handle, looks up an MDCACHE entry with an active promoted ref, treats cache miss as success, clears trust bits, performs requested close/parent/ACL cleanup, then unrefs. Attribute update validates that immutable identity fields are not changed, filters flags, looks up the entry, handles zero link count by invalidating content and closing, updates only trusted cached attributes, and clears attribute trust when no meaningful update was possible.

Try-release is latch-based: it keeps the hash partition locked, checks refcount, takes a temp ref if the entry is otherwise idle, removes the hash entry, releases the latch, then drops the temp ref to allow cleanup.

Pass-through state notifications do not consume cache content; they set context and call the corresponding upper vector function.

## State and Persistence Behavior
Upcalls mutate volatile cache state: trust flags, cached attributes, cached ACL/fs_locations/sec_label ownership, parent-handle cache, hash reachability, and open FD state. They do not persist data, but they reflect lower-FSAL change notifications so future NFS operations see fresh metadata or miss the cache.

## Dependencies and Integration Points
This file integrates with lower-FSAL upcall registration from `mdcache_main.c`, MDCACHE hash lookup, LRU references, FSAL close, NFS ACL and fs_locations memory management, state/delegation/layout notification paths, general async invalidation fridge, and export/op-context lifetime helpers.

## Risks and Edge Cases
Important risks include missing `release_op_context()` on all paths, updating attributes that are not currently trusted, ownership transfer of ACL/fs_locations/sec_label payloads, clearing the right trust flags for directory changes, races between try-release and new lookups, and handling upcalls during export teardown. In `mdc_up_update()`, incremental timestamp flags must only move cached times forward when requested.

## Test Signals
Test cache miss invalidation as success, invalidate-close closing open cached objects, parent and ACL invalidation, zero-link updates, each incremental attribute update flag, immutable attribute rejection, try-release success with sentinel-only refs and failure with active refs, async invalidate-close scheduling, and pass-through lock/layout/delegation callbacks with correct context.
