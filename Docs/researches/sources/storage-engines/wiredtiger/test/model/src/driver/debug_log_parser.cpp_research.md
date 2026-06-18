# sources/storage-engines/wiredtiger/test/model/src/driver/debug_log_parser.cpp

Purpose: replays WiredTiger debug logs, either binary log scan or `wt printlog -u` JSON, into the model database so recovered WT state can be verified against modeled history.

Important APIs and functions: JSON `from_json` overloads decode log operation structs; binary `from_debug_log` overloads call WiredTiger internal unpackers for col/row put/remove/truncate, timestamps, prev LSN, and commit headers. `metadata_apply` interprets metadata row puts, maps file IDs to files/tables, creates model tables from colgroups/table/file metadata, tracks checkpoint metadata, and updates base write generation. `metadata_checkpoint_apply` creates WT-style checkpoint snapshots. `apply` overloads perform model operations for row/column changes and transaction timestamps. Static `from_debug_log` uses `__wt_log_scan`; static `from_json` parses a JSON array.

Control flow and state: parser state maps file IDs/files/tables, stores metadata configs, accumulates per-transaction checkpoint metadata, and tracks base write generation. Commit records begin a model transaction, replay operations, then finalize; system `prev_lsn` may trigger `database.start`.

Dependencies and integration: depends on nlohmann JSON, `wt_internal.h`, model database/table/transaction APIs, `decode_utf8`, and config parsing. Used by model verification tools.

Risks and test signals: unsupported log operations such as modify variants throw. Metadata support is intentionally narrow and rejects column groups with extra nesting. Correct signals are successful replay followed by `database.start()` and table verification matching actual WiredTiger files.
