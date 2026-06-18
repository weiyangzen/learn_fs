# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp

Purpose: Broad regression tests for rollback-related sub-level errors in eviction, transaction blocking, modify reconstruction, and write conflicts.

Important APIs/types: `__wt_evict_app_assist_worker_check`, `__wti_evict_app_assist_worker`, `__txn_modify_block`, `__wt_txn_is_blocking`, `__wt_modify_reconstruct_from_upd_list`, `WT_ROLLBACK`, and sub-level codes `WT_CACHE_OVERFLOW`, `WT_OLDEST_FOR_EVICTION`, `WT_WRITE_CONFLICT`, `WT_MODIFY_READ_UNCOMMITTED`.

Control flow: sections configure internal connection cache/eviction state, txn mod counts, shared txn ids, operation timeout, transaction isolation, and update chains. They assert no error for safe eviction cases and prepared/unsupported blocking cases; assert `WT_ROLLBACK` with oldest-for-eviction when the transaction pins oldest id; assert cache overflow when app eviction times out; assert write conflict for invisible update; and assert read-uncommitted modify reconstruction rollback.

State and persistence: creates/drops a table for cursor/cache and write-conflict setup. Mutates connection cache, eviction flags, transaction snapshot fields, dhandle allocation, and `WT_UPDATE` structures.

Dependencies/integration: very coupled to internal eviction/transaction visibility code. Risks include fragile manual state fabrication and cleanup requirements. Test signals are return codes and exact `WT_ERROR_INFO`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_rollback.cpp -->
