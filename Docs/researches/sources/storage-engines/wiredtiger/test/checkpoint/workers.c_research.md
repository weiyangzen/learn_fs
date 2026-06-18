# sources/storage-engines/wiredtiger/test/checkpoint/workers.c

Purpose: Implements the worker side of the checkpoint stress test: table creation, worker-thread startup, random transactional updates across all configured tables, and timestamp/prepared-transaction behavior used by compatibility and recovery validation.

Important APIs/types/functions: `start_workers` initializes modify replacement data, creates tables via `create_table`, starts `g.nworkers` threads, and joins them. `worker` is the thread entry point, while `real_worker` owns the session, cursor array, transaction loop, timestamp handling, and cursor reopen behavior. `worker_op`, `worker_no_ts_delete`, and `modify_build` encapsulate per-key data operations.

Control flow: tables are created before worker launch; each worker opens a snapshot-isolation session and one cursor per table, then loops until `g.opts.running` is false or `g.nops` is reached unless a stop timestamp is configured. Each iteration picks a key in the thread's key range, optionally performs a no-timestamp delete transaction, performs the same logical operation on every table, and periodically commits or rolls back. Timestamp mode may use global clock locking or deterministic reserved timestamps for predictable replay; prepared transactions get prepare/durable/commit or rollback timestamps.

State and persistence: creates WiredTiger tables using row or column key format, optionally disabling logging for timestamped tests and using disaggregated layered tables. Persistent table data is intentionally stressed through inserts, modifies, range removes, checkpoints, rollbacks, prepared transactions, and cursor reopen paths. Global state comes from `g`, including timestamp locks, stable timestamp, operation count, table cookies, and worker thread data.

Dependencies/integration: depends on `test_checkpoint.h`, WiredTiger sessions/cursors, `test_util`, WT thread helpers, and global checkpoint-test options. The compatibility release script invokes the checkpoint binary to generate and verify data across branches.

Risks and test signals: key risks are timestamp-ordering bugs, inconsistent cross-table transactions, missed `WT_ROLLBACK`/`WT_PREPARE_CONFLICT` handling, cursor state bugs after range removes, and unsafe interaction with oldest/stable movement. Progress prints, fatal `testutil_check` assertions, verification mode in the checkpoint binary, and cross-version compatibility runs are the primary signals.
