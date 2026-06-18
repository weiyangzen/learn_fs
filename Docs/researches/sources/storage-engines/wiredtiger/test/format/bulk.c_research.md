# sources/storage-engines/wiredtiger/test/format/bulk.c

## Purpose
`bulk.c` loads initial table content for format tests. It supports normal bulk append, non-bulk insert fallback, mirrored table loading from a base cursor, timestamped transaction batches, adaptive row-count reduction on cache pressure, and an initial checkpoint for durability.

## Important APIs, Types, And Functions
The public entry point is `void wts_load(void)`. Core helpers are `table_load`, `bulk_begin_transaction`, `bulk_commit_transaction`, and `bulk_rollback_transaction`. It uses `TABLE`, `SAP`, `WT_CURSOR`, `WT_ITEM`, key/value generation helpers, `read_op`, `wt_wrap_open_cursor`, timestamp helpers, `config_single`, and `config_print`.

## Control Flow
`wts_load` loads the single table or, in multi-table mode, first loads the base mirror and then each remaining table. `table_load` opens a session, optionally opens the base mirror cursor, decides whether `bulk,append` is legal, initializes key/value buffers, optionally begins a timestamped transaction, and iterates through configured rows. Row-store keys are generated; values either come from `val_gen` or the base mirror. Inserts are traced when bulk tracing is enabled. On `WT_CACHE_FULL` or `WT_ROLLBACK` for non-mirror loads, it rolls back any active batch, reduces insert/write percentages in favor of deletes, and shortens the configured row count.

## State And Persistence Behavior
Successful inserts populate WiredTiger tables. Timestamped loads advance `g.timestamp`, assign read/commit timestamps, and call `timestamp_once` so oldest/stable timestamps move and cache is not pinned. If the load exits early, it rewrites `runs.rows` in the in-memory config and persists a new `CONFIG`. After loading, `table->rows_current` is initialized and non-in-memory runs take a checkpoint.

## Dependencies And Integration Points
Bulk loading depends on configuration normalized by `format_config.c`, disaggregated-storage state, mirror configuration, transaction timestamp configuration, and value/key generators. It integrates with later operation threads by establishing `rows_current`, with mirror verification by making mirrored tables byte-compatible, and with recovery by checkpointing loaded data.

## Risks And Test Signals
Important risks are using bulk load with reverse collators or disaggregated storage, mismatched mirror loads, timestamp batches pinning cache, and silent row-count drift after cache-full handling. Test signals include progress tracking every early 10 rows or later 5K rows, trace bulk records, row-count rewrites in `CONFIG`, and assertion failures if a mirrored table cannot load matching rows.
