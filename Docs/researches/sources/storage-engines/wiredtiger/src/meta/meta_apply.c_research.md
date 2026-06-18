# sources/storage-engines/wiredtiger/src/meta/meta_apply.c

## Purpose
Provides a schema-lock-protected iterator that applies callbacks to every btree file entry in WiredTiger metadata, skipping the metadata file itself.

## Important APIs, Types, and Functions
The exported helper is `__wt_meta_apply_all`. Its worker `__meta_btree_apply` accepts a `file_func`, optional `name_func`, and config array. It operates over `WT_CURSOR` metadata entries and temporarily pins matching data handles with `__wt_session_get_dhandle`.

## Control Flow
`__wt_meta_apply_all` asserts the schema lock, obtains a metadata cursor, and delegates iteration. For each metadata key, the worker skips `file:WiredTiger.wt`, calls `name_func` to decide whether to skip, ignores non-btree prefixes, then opens the handle. Busy handles are tolerated with `WT_TRET_BUSY_OK`; successful opens run `file_func` with the dhandle saved/restored and then release the handle.

## State and Persistence Behavior
The file itself writes no metadata. It pins and releases data handles so callbacks can safely inspect or mutate btree state without the handle being concurrently dropped. Persistence effects depend entirely on the supplied callback.

## Dependencies and Integration Points
It integrates metadata cursor access, schema lock discipline, data-handle cache management, and bulk operations such as checkpoint, verification, or schema scans that need to visit all btrees.

## Risks and Edge Cases
The iterator accumulates errors while continuing to the end, so callers must inspect the final return. Busy handles are skipped rather than fatal, which is correct for some global operations but can hide work not performed. Callback code runs with the target dhandle active and must respect the surrounding schema-lock assumptions.

## Test Signals
Tests that run checkpoint or metadata-wide operations while handles are busy, bulk-loading, or being verified should show skips rather than crashes. Error aggregation can be tested with callbacks that fail for selected entries.
