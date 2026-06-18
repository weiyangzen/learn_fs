# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table.h

Purpose: declares `kv_table`, the sorted key-value table model with timestamped versions, transactional write APIs, non-transactional convenience APIs, rollback-to-stable, and WT verification.

Important APIs and types: `kv_table_type` (`column`, `row`), `kv_table_config` (`log_enabled`, `type`), `kv_table::type_by_key_value_format`, name/type/format accessors, `timestamped`, `contains_any`, `get`/`get_ext`, `insert`, `update`, `remove`, `truncate`, `fix_timestamps`, `rollback_updates`, `clear`, `rollback_to_stable`, `verify`, `verify_noexcept`, and `verify_cursor`.

Control flow: table operations resolve or create `kv_table_item` entries in a sorted `std::map`. Transactional writes create `kv_update` objects tied to a transaction, add them to the item chain, and register them with the transaction. Non-transactional APIs use `with_transaction` to create a short transaction and commit/rollback. Reads delegate visibility to `kv_table_item`. Verification builds a `kv_table_verify_cursor` and compares WT cursor output.

State and persistence: `_data` is sorted by `data_value` and intentionally never removes map entries so references remain stable after releasing the table map lock. Each key's versions live in `kv_table_item`. `_config.log_enabled` disables timestamp semantics by forcing timestamps to none.

Dependencies and integration: includes `data_value.h`, `kv_table_item.h`, `kv_update.h`, `verify.h`, and `wiredtiger.h`; holds a `kv_database &` for transaction creation and disaggregated config. Used by runners, debug parser, and tests.

Risks: key/value formats must be set before WT integration calls `key_format()`/`value_format()`. Map entries are retained after removal, so long tests can accumulate tombstone items. `verify_cursor` is explicitly not thread-safe. Non-timestamped tables silently rewrite update timestamps to none.

Test signals: table tests compare model and WT behavior for insert/update/remove/truncate, overwrite false, row and column formats, timestamps, checkpoints, prepared conflicts, rollback, RTS, and verification failure cases.
