# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_export.c

## Purpose

This file implements MDCACHE export operations. Most filesystem capability and quota/pNFS queries pass through to the sub-FSAL, while unexport/unmount/release perform MDCACHE-specific export-map cleanup and LRU drain synchronization. The source was read as a complete 1051-line file.

## Important APIs, Types, and Functions

Important functions include `mdcache_get_name`, `mdcache_unexport`, `mdcache_unmount`, `mdcache_drain_export_cleanup`, `mdcache_exp_release`, `mdcache_get_dynamic_info`, many `mdcache_fs_*` wrappers, quota wrappers, pNFS device/layout wrappers, `mdcache_wire_to_host`, `mdcache_host_to_key`, `mdcache_alloc_state`, `mdcache_is_superuser`, `mdcache_prepare_unexport`, and `mdcache_export_ops_init`.

## Control Flow

Unexport marks the export with `MDC_UNEXPORT`, walks `entry_list`, takes active refs, removes `entry_export_map` links under the documented `attr_lock` then `mdc_exp_lock` order, closes stale global FDs, clears `first_export_id`, and schedules export-less entries for LRU cleanup. Unmount performs the same map removal for junction entries. Release waits until `cleanup_pending` drains, stops dirmap LRU, releases the sub-export, detaches export ops, destroys locks, and frees memory. Other operations call the corresponding sub-export op through `subcall_raw`.

## State and Persistence Behavior

State includes export flags, export-entry maps, cleanup counters, dirmap state, name strings, mutexes, and sub-export references. Persistence is not on disk; cleanup protects against dangling in-memory FDs/export pointers after export teardown.

## Dependencies and Integration Points

The file depends on FSAL export ops, export manager state, MDCACHE LRU/hash helpers, config parsing, quota/mount helpers, and the lower FSAL export vector. `mdcache_export_ops_init` is the integration point that publishes the wrapper export vector.

## Risks and Edge Cases

Lock ordering is critical. Cleanup intentionally cannot hold `attr_lock` across LRU cleanup queue push. Multi-export entries must update `first_export_id` and close global FDs without evicting sibling exports. `mdcache_drain_export_cleanup` can wait indefinitely if cleanup counters are leaked.

## Test Signals

Test single and nested export unexport, junction unmount, active NFSv3 FD cleanup, entries shared by multiple exports, sub-FSAL pass-through capability queries, pNFS/quota wrappers, and release waiting for LRU cleanup completion.
