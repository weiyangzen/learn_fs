# sources/storage-engines/wiredtiger/src/block_cache/block_mgr.c

## Purpose

`block_mgr.c` builds the `WT_BM` method table used by the B-tree layer and adapts generic block-manager operations to file-backed, read-only checkpoint, tiered multi-handle, block-cache, compaction, salvage, verify, and sync behavior.

## Important APIs, Types, and Functions

Externally visible functions are `__wti_bm_close_block`, `__wt_bm_sweep_handles`, `__wti_bm_method_set`, and `__wt_bm_set_readonly`. Private method implementations cover address validation/stringification, checkpoint lifecycle, close, compaction, encryption skip, free, mapped-state, read, salvage, stat, tiered object switching, sync, verify, write, write-size, and truncation checks. Important fields include `WT_BM.block`, `prev_block`, `next_block`, `handle_array`, `is_live`, `is_multi_handle`, `map`, and `max_flushed_objectid`.

## Control Flow

`__wti_bm_method_set` installs normal methods, then replaces mutating methods with read-only stubs for checkpoint handles. Normal reads and writes delegate to `__wt_bm_read` and `__wt_block_write`; free removes cached blocks then frees file space. Checkpoint load marks live versus checkpoint handles, loads block checkpoint metadata, optionally maps read-only single-file checkpoints, and switches the method table to read-only for checkpoint handles.

Tiered switching opens the requested object, loads its checkpoint, marks the current block for sync, and delays the active-handle swap until checkpoint write when eviction is disabled. Sync ensures pending switches have happened, fsyncs previous tiered handles as needed, and handles `prev_block`. Sweeping closes non-active tiered handles whose read count is zero and whose object ID is older than the maximum flushed object.

## State and Persistence Behavior

The file mutates `WT_BM` runtime method pointers and tiered handle arrays, reference counts in `WT_BLOCK`, `sync_on_checkpoint`, `prev_block`/`next_block`, mapped-region state, and `max_flushed_objectid`. Durable effects occur through delegated checkpoint, write, free, compact, salvage, fsync, and truncate operations.

## Dependencies and Integration Points

It integrates file-backed block APIs, block cache removal, mapping, tiered handle helpers, checkpoint code, compaction, salvage, verify, the B-tree `WT_BM` interface, connection block hash, checkpoint lock, capacity throttling, and filesystem fsync.

## Risks and Edge Cases

Read-only method replacement is a safety boundary for checkpoint handles. Tiered object switches are intentionally delayed; missing the checkpoint-time switch triggers an assertion in sync. Sweeping uses an array and `memmove`, noted as potentially slow with many handles. Closing a block during checkpoint is disallowed except panic-on-failure state. Cached block removal must happen before freeing disk space to avoid stale reads.

## Test Signals

Tests should exercise method-table read-only behavior, checkpoint load/unload mapping, tiered switch scheduling and completion, fsync of previous active tiered files, handle sweeping after last reader release, block-cache removal on free, compaction/salvage/verify readonly stubs, and `can_truncate` forwarding to available extents.
