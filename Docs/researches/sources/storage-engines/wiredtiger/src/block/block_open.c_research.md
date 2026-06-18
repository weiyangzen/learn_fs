# sources/storage-engines/wiredtiger/src/block/block_open.c

## Purpose

`block_open.c` creates, opens, closes, drops, and sizes WiredTiger block files. It owns descriptor-block read/write validation, block-handle sharing through the connection block hash, open-time allocation configuration, file-system flags, live-restore metadata attachment, and basic block statistics.

## Important APIs, Types, and Functions

Public entry points include `__wt_block_manager_drop`, `__wt_block_manager_drop_object`, `__wt_block_manager_create`, `__wt_block_close`, `__wti_block_configure_first_fit`, `__wt_block_open`, `__wti_desc_write`, `__wt_block_stat`, `__wt_block_manager_size`, and `__wt_block_manager_named_size`. The private `__desc_read` validates the first allocation-sized descriptor block, and `__file_is_wt_internal` distinguishes metadata/history-store files for salvage-oriented errors.

## Control Flow

Creation opens a new durable exclusive file, renames unexpected leftovers aside with numeric suffixes, writes the descriptor, fsyncs, closes, and removes the file on error. Open first searches `conn->blockhash` under `conn->block_lock` for an existing `WT_BLOCK` matching filename and object ID. If absent, it allocates and configures a new handle, opens the file, attaches live-restore metadata to the file handle, records current file size, initializes `live_lock`, verifies the descriptor unless forced salvage is requested, then inserts the handle into the connection hash.

`__desc_read` reads the descriptor block, performs endian-aware checksum validation, checks magic and supported major/minor versions, handles rollback-to-stable by returning `ENOENT` for too-small/corrupt files, and marks connection data corruption for general corruption cases.

## State and Persistence Behavior

The descriptor block is the durable file identity record: magic, block major/minor versions, allocation-size-sized checksum, and endian-normalized layout. Open initializes `WT_BLOCK` fields such as `name`, `objectid`, `allocsize`, `allocfirst`, `os_cache_max`, `os_cache_dirty_max`, `extend_len`, `size`, `readonly`, and `created_during_backup`. Handles are reference-counted and shared until `__wt_block_close` destroys locks, checkpoint state, file handles, and memory.

## Dependencies and Integration Points

This file sits under the block-cache open path, tiered-object open path, live restore, the WiredTiger file-system API, config parsing, connection block-hash locking, incremental backup, rollback-to-stable, import repair, and data-source statistics. `__wti_desc_write` is also used by salvage to reset the file descriptor.

## Risks and Edge Cases

Open error handling must unlock `conn->block_lock` and close partially initialized handles. Descriptor validation intentionally behaves differently for rollback-to-stable, internal files, import repair, and forced salvage. Renaming unexpected files on create handles non-transactional schema leftovers but can surprise external users writing in WiredTiger's namespace. `allocfirst` is an atomic counter because multiple operations can request first-fit allocation concurrently.

## Test Signals

Signals include descriptor checksum/magic/version failures, create with leftover files, forced salvage skipping descriptor reads, rollback-to-stable corrupt-file paths, first-fit configuration races, and statistics populated by `__wt_block_stat` (`allocation_size`, `block_checkpoint_size`, `block_reuse_bytes`, and `block_size`).
