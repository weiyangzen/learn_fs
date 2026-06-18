# sources/storage-engines/wiredtiger/src/meta/meta_ext.c

## Purpose
Exposes selected metadata operations through the extension/public API boundary.

## Important APIs, Types, and Functions
The extension wrappers are `__wt_ext_metadata_insert`, `__wt_ext_metadata_remove`, `__wt_ext_metadata_search`, and `__wt_ext_metadata_update`, all taking `WT_EXTENSION_API` plus an optional `WT_SESSION`. Public utility entry points are `__wt_metadata_get_ckptlist` and `__wt_metadata_free_ckptlist`, exported for the `wt list` tool.

## Control Flow
Each extension wrapper maps `wt_api->conn` to `WT_CONNECTION_IMPL`, falls back to `conn->default_session` when the caller passes `NULL`, then delegates to the internal metadata function. Checkpoint-list retrieval delegates to `__wt_meta_ckptlist_get` and freeing delegates to `__wt_ckptlist_free`.

## State and Persistence Behavior
Insert/update/remove wrappers can modify metadata and therefore durable schema/checkpoint state. Search returns an allocated copy that the caller must free. The checkpoint-list API allocates a `WT_CKPT` array and expects callers to release it through the matching free function.

## Dependencies and Integration Points
This file bridges `wiredtiger_ext.h` users and internal metadata APIs. Examples and extensions that demonstrate metadata operations depend on this wrapper layer instead of directly including internal symbols.

## Risks and Edge Cases
Using the default session when `wt_session` is `NULL` is convenient but can bypass caller-specific isolation or error context. Extension callers must obey metadata locking expectations even though this layer does not acquire schema locks itself. Search allocation ownership is explicit and easy to leak.

## Test Signals
Extension API examples that insert/search/update/remove metadata exercise these wrappers. `wt list` and checkpoint-list listing paths validate the exported checkpoint-list functions.
