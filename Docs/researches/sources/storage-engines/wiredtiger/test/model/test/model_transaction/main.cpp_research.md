# sources/storage-engines/wiredtiger/test/model/test/model_transaction/main.cpp

## Purpose
This executable validates transaction semantics in the WiredTiger model and compares them with real WiredTiger behavior. It covers snapshot isolation, write conflicts, read timestamps, commit timestamp changes within a transaction, prepared transactions, logged table timestamp behavior, column-store transaction behavior, rollback, reset snapshot, and truncation interactions with visibility and conflicts.

## Important APIs, Types, and Functions
Primary APIs include `model::kv_database::begin_transaction`, `model::kv_transaction::commit`, `rollback`, `prepare`, `set_commit_timestamp`, `reset_snapshot`, and table methods `insert`, `remove`, `truncate`, `get`, and `get_ext`. WT comparison uses helpers such as `wt_model_txn_begin_both`, `wt_model_txn_insert_both`, `wt_model_txn_prepare_both`, `wt_model_txn_commit_both`, `wt_model_txn_rollback_both`, `wt_model_txn_reset_snapshot_both`, and `wt_model_truncate_both`. Scenarios include basic, column-store, prepared, logged, visible-truncate, and conflict-truncate variants.

## Control Flow
The model-only scenarios build concurrent transactions and directly inspect table state and return codes. WT scenarios recreate the same sequences with two or more `WT_SESSION`s, then call model/WT paired helpers and final `verify_noexcept`. `main` runs all scenarios after parsing `test_util` options and cleans the test home unless preservation is requested.

## State, Persistence, and Integration
The file models transaction-private writes, committed history, read timestamp visibility, conflict detection against concurrent and snapshot-invisible writes, prepared state and prepare conflicts, logged tables where timestamps are ignored and prepare is unsupported, and column-store recnos. Truncation tests verify two edge behaviors: truncate skips records invisible to its transaction, and truncate fails with `WT_ROLLBACK` when it encounters uncommitted conflicting updates. WT integration uses row-store and column-store table formats and debug-log verification for the broad transaction paths.

## Risks and Test Signals
The highest-risk areas are timestamp assignment order within a transaction, prepared transaction read conflicts, and places where the test intentionally omits WT operations that would hang or abort. Logged table semantics are deliberately different from non-logged tables, so regressions may look like timestamp mismatches unless the table config is considered. Test signals include exact return-code parity, `WT_ROLLBACK`, `WT_PREPARE_CONFLICT`, exception assertions for illegal model operations, final table verification, and debug-log replay for the main transaction scenarios.
