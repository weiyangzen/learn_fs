# sources/storage-engines/wiredtiger/src/block_cache/block_tier.c

## Purpose

`block_tier.c` opens and manages block handles for tiered storage objects. It resolves local versus shared-object names, opens remote bucket-backed objects when not present locally, manages the `WT_BM` tiered handle array, and tracks active readers so old object handles can be swept safely.

## Important APIs, Types, and Functions

Key functions are `__wti_blkcache_tiered_open`, `__wt_blkcache_get_handle`, `__wti_blkcache_get_read_handle`, and `__wt_blkcache_release_handle`. Private `__blkcache_find_open_handle` searches a `WT_BM` handle array and optionally increments `WT_BLOCK.read_count`.

Important types and fields are `WT_TIERED.current_id`, `WT_TIERED.tiers`, `WT_BUCKET_STORAGE`, `WT_BM.handle_array`, `handle_array_lock`, and `WT_BLOCK.remote`.

## Control Flow

Tiered open treats URI-based opens as the current local object and object-ID opens as historical objects. Current objects use the local `file:` tier and open read-write. Historical objects derive an `object:` URI, load metadata, check for a local copy, and otherwise compose `bucket_prefix + object_name`, switch into bucket storage, open read-only/fixed, and mark the block remote.

`__wt_blkcache_get_handle` first searches under a read lock. On miss it opens a new handle without holding the array write lock, then takes the write lock, checks for a racing insert, and appends the new handle or closes the duplicate. Read acquisitions increment `read_count`; release decrements and reports whether this was the last reader.

## State and Persistence Behavior

This file does not write data pages directly. It mutates runtime block-handle arrays, per-handle read counts, and remote/read-only flags. Opening remote objects may access bucket storage and local metadata. It relies on metadata configuration to locate objects and bucket prefixes.

## Dependencies and Integration Points

It is used by `block_cache.c` open for tiered trees, `block_read.c` for multi-handle reads, and `block_mgr.c` for tiered switching/sweeping. It depends on tiered metadata naming, bucket-storage file systems, `__wt_block_open`, read/write locks, and block close.

## Risks and Edge Cases

Current-object opens assert that racing `current_id` changes are impossible except under checkpoint-lock protection. The open-without-array-lock path avoids blocking but must close duplicate handles after races. Historical remote objects are read-only. Read-count correctness controls when old handles can be swept; leaks prevent cleanup and premature release risks closing a handle under readers.

## Test Signals

Tests should cover local current-object open, historical object open from local cache, remote bucket open with prefix, racing handle insertion, read-count last-release behavior, and sweeping eligibility after `max_flushed_objectid` advances.
