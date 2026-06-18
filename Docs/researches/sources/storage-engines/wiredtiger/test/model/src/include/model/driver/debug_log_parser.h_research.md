# sources/storage-engines/wiredtiger/test/model/src/include/model/driver/debug_log_parser.h

Purpose: declares `model::debug_log_parser`, the adapter that reconstructs an in-memory `kv_database` from WiredTiger debug log records or a JSON printlog file. It is used after opening a database and before further writes, because the log may not describe most recent in-memory operations otherwise.

Important APIs and types: nested record structs model log entries (`col_put`, `col_remove`, `col_truncate`, `row_put`, `row_remove`, `row_truncate`, `commit_header`, `prev_lsn`, `txn_timestamp`). Static entry points `from_debug_log(kv_database &, WT_CONNECTION *)` and `from_json(kv_database &, const char *)` populate a database. Instance `apply` overloads map row/column puts, removes, truncates, timestamp records, and LSN records into model transactions and tables. `begin_transaction`, `commit_transaction`, `metadata_apply`, `metadata_checkpoint_apply`, and `table_by_fileid` support transaction and metadata reconstruction.

Control flow: callers invoke a static loader, which creates a parser, reads log entries, begins a model transaction from each commit header, applies operation records to that transaction, records timestamps, and commits/finalizes the transaction. Metadata row puts are handled specially to build table/file/checkpoint indexes before data records can be resolved by file ID.

State and persistence: the parser owns no database lifetime; it stores a reference to `kv_database`. Internal maps track metadata config maps, file-to-colgroup names, file-to-file IDs, file ID to file/table names, resolved file ID to `kv_table_ptr`, current base write generation, and accumulated checkpoint metadata keyed by transaction ID and checkpoint name. This mirrors persistent WiredTiger metadata into transient model state.

Dependencies and integration: includes `model/kv_database.h`, `model/util.h`, and `wiredtiger.h`. It integrates with `wt_print_debug_log` and `verify_using_debug_log` in test utilities, plus `kv_transaction::set_wt_metadata` and `kv_update::set_wt_transaction_metadata` for WT transaction identity.

Risks: correctness depends on metadata records being seen before data records that use their file IDs. The table/file ID maps are mutable parser state and are not advertised as thread-safe. Debug log import can be stale if called after additional writes. Buffer/config parsing errors or missing metadata produce model exceptions rather than partial verification.

Test signals: `verify_using_debug_log` opens a logged WT database, loads the model through both `from_debug_log` and JSON `from_json`, verifies every table against WT, and compares oldest/stable timestamps. A negative path injects a bogus model row and expects verification to fail.
