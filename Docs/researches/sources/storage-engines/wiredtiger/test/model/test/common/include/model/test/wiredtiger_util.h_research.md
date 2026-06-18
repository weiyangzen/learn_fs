# sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/wiredtiger_util.h

Purpose: declares WT-side test helper functions and macros that mirror model operations and assert model/WT equivalence.

Important APIs and types: functions `wt_get`, `wt_insert`, `wt_remove`, `wt_truncate`, `wt_update`; transaction helpers `wt_txn_begin`, `wt_txn_commit`, `wt_txn_prepare`, `wt_txn_reset_snapshot`, `wt_txn_rollback`, `wt_txn_set_commit_timestamp`, `wt_txn_get`, `wt_txn_insert`, `wt_txn_remove`; checkpoint/timestamp/debug helpers `wt_ckpt_get`, `wt_ckpt_create`, `wt_get_timestamp`, `wt_set_timestamp`, `wt_get_oldest_timestamp`, `wt_set_oldest_timestamp`, `wt_get_stable_timestamp`, `wt_set_stable_timestamp`, `wt_print_debug_log`, `wt_rollback_to_stable`; assertion and paired-operation macros.

Control flow: helper functions wrap WT sessions/cursors/transactions and return WT error codes for expected conflicts/not-found/rollback cases. Macros perform the same operation on model and WT, then compare return codes and values.

State and persistence: the helpers mutate the WT database via sessions and transactions. Macros rely on in-scope names such as `database`, `conn`, and `session`. Timestamps and checkpoints persist in WT metadata.

Dependencies and integration: includes `data_value.h`, `kv_database.h`, `wiredtiger.h`, and `test_util.h`. Implemented by `common/wiredtiger_util.cpp` and used by model unit tests.

Risks: macro scope assumptions can produce confusing errors. Helpers treat selected WT return codes as expected while `testutil_check` aborts on others. Config buffers are fixed-size in implementations. Paired macros must preserve operation order exactly to avoid model/WT divergence.

Test signals: these helpers are themselves exercised by all model/WT comparison tests; failures show as assertion differences in return codes or `data_value` output.
