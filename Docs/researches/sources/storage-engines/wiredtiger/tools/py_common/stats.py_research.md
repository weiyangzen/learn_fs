# sources/storage-engines/wiredtiger/tools/py_common/stats.py

Purpose: stores and emits per-page decode statistics for keys, timestamp metadata, durable timestamp metadata, and transaction IDs.

Important APIs and control flow: `PageStats` is a dataclass with counters and byte-size accumulators for keys, durable start/stop timestamps, start/stop timestamps, and start/stop transaction ids. Computed properties `num_ts`, `ts_sz`, `num_txn`, and `txn_sz` aggregate related counters. `csv_cols()` and `to_csv_cols()` define the CSV schema. `outfile_stats_start()` and `outfile_stats_end()` write block/page/stat columns to an optional output handle. `process_timestamps()` inspects parsed cell attributes with `getattr()` and increments the relevant counters and sizes.

State and persistence behavior: instances are mutable accumulators attached to a decoded page. Optional CSV writing is the only external side effect.

Dependencies and integration points: `btree_format.Cell.process_timestamps()` and `WTPage` populate these stats, while `file_format.wtdecode_file_object()` writes them when `--csv` is passed.

Risks: CSV schema alignment depends on `file_format.outfile_header()` matching `outfile_stats_end()`. Prepared update fields are present but marked as not currently reported in comments. `process_timestamps()` relies on dynamic cell attributes, so missing or renamed fields silently count as absent.

Test signals: no direct unit test in this subset validates CSV output. Indirect signal is non-null `page.pagestats` during successful page decode and stable CSV column count when `--csv` is used.
