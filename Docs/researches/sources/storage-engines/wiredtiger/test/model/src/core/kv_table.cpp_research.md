# sources/storage-engines/wiredtiger/test/model/src/core/kv_table.cpp

Purpose: implements table-level operations for the in-memory key/value model, including timestamp-aware reads, writes, truncation, rollback-to-stable, and verification cursor creation.

Important APIs and functions: `type_by_key_value_format` detects column-store tables from `key_format == "r"`. `get/get_ext` read directly, through checkpoints, or through transactions. `insert`, `update`, `remove`, and `truncate` create `kv_update` objects and attach them to `kv_table_item`s and transactions. Non-transactional variants run through `with_transaction` and `kv_transaction_guard`. `fix_timestamps` and `rollback_updates` delegate to items by key.

Control flow and state: `_data` is a sorted `std::map<data_value, kv_table_item>` protected by `_lock`, but items are never removed to keep returned references stable. Logged/non-timestamped tables normalize timestamps to `k_timestamp_none`. Truncate scans ranges and also checks neighboring prepared updates for known issue `WT-13232`.

Dependencies and integration: depends on `kv_database`, `kv_transaction`, `kv_table_item`, `kv_update`, and verification classes. Workload runners call this for model execution.

Risks and test signals: never removing map elements preserves references but can retain deleted key shells. Truncate prepared-conflict behavior is explicitly tied to a known WiredTiger issue. Signals are model/WiredTiger return-code equivalence and table verifier agreement.
