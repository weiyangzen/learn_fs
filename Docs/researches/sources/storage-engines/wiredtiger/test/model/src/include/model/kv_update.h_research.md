# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_update.h

Purpose: declares the stored version object for a table item, carrying value, timestamps, transaction state, and WT debug-log transaction metadata.

Important APIs and types: comparators `commit_timestamp_comparator` and `prepare_timestamp_comparator`; constructors for timestamped standalone update and transaction-backed update; comparison operators; `value`, `global`, `commit_timestamp`, `durable_timestamp`, `committed`, `prepared`, `txn`, `txn_id`, `txn_state`, `set_timestamps`, `remove_txn`, `set_wt_transaction_metadata`, `wt_txn_id`, and `wt_base_write_gen`.

Control flow: table writes create updates with either immediate timestamps or a transaction pointer. Visibility checks inspect commit/durable timestamps, transaction state, snapshot membership, and prepared state. Commit repairs timestamps, then may drop the transaction pointer through `remove_txn` while preserving transaction ID. Debug-log import sets WT metadata for WT snapshot emulation.

State and persistence: stores commit timestamp, durable timestamp, `data_value`, model transaction ID, optional `kv_transaction_ptr`, WT transaction ID, and WT base write generation. A value of `NONE` represents deletion/tombstone. `global()` means non-timestamped update.

Dependencies and integration: includes `data_value.h` and `kv_transaction.h`. Used by `kv_table_item`, `kv_transaction`, and `kv_transaction_snapshot`.

Risks: `operator<` returns true after all equality-like comparisons fall through, which is unusual and relies on callers checking equality separately; changes could affect sorted update chains. Prepared comparator uses prepare timestamp when available. Dropping the transaction pointer too early would lose state needed by prepared/commit checks.

Test signals: tests should cover update ordering by commit timestamp, duplicate timestamp/value cases, prepared visibility, durable timestamp checkpoint reads, global updates for logged tables, transaction pointer removal after commit, and WT metadata snapshot behavior.
