# Research: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h

## sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h

Purpose: Shared declarations, constants, and global state for the checkpoint stress test.

Important types/constants: `URI_BASE`, `ERR_KEY_MISMATCH`, `ERR_DATA_MISMATCH`, `table_type` enum (`MIX`, `ROW`, `COL`), `RESERVED_TIMESTAMPS_FOR_ITERATION`, `PRED_REPLAY_STABLE_PERIOD`, `COOKIE`, `THREAD_DATA`, and `GLOBAL`.

State model: `GLOBAL` contains shared `TEST_OPTS`, home, checkpoint name, connection, debug flag, key/op/table/worker counts, log/status, timing-stress booleans, timestamp state (`ts_oldest`, `ts_stable`, `stop_ts`), prepare/replay options, table cookies, thread data, clock lock, and service thread handles. `THREAD_DATA` stores per-thread id, key range, latest timestamp, and random states.

Dependencies/integration: includes `test_util.h` and declares functions implemented across `test_checkpoint.c`, `checkpointer.c`, and `workers.c`: thread lifecycle, logging, tiered delay, worker start, table type formatting, consistency verification, and prepare discovery.

Risks/test signals: this header centralizes global mutable state shared by many threads, so concurrency correctness depends on disciplined locking/atomic behavior in implementation files. It also fixes timestamp reservation formulas used by predictable replay. Signals are indirect through all checkpoint executable variants.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.h -->
