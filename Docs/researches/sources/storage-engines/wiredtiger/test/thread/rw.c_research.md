# sources/storage-engines/wiredtiger/test/thread/rw.c

## Purpose

`rw.c` drives concurrent read/write operations for the thread stress test. It allocates per-thread state, starts reader and writer threads, verifies resulting files, and prints operation counts.

## Important APIs, Types, and Functions

Key types/functions are `INFO`, `rw_start`, `reader_op`, `reader`, `writer_op`, `writer`, and `print_stats`. It uses WiredTiger sessions/cursors, random state, thread helpers, and global options such as `multiple_files`, `session_per_op`, `vary_nops`, `max_nops`, and `log_print`.

## Control Flow

`rw_start` prepares writer and reader `INFO` entries, creates/loads files, starts reader and writer threads, joins them, reports throughput, verifies each file, prints stats, and frees allocations. Reader threads search random keys; writer threads remove keys divisible by five and update others. Each thread either reuses one session/cursor or opens a session per operation.

## State and Persistence Behavior

State includes shared `run_info`, per-thread random generators and counters, table data mutated by concurrent removes/updates, optional log records, and final verified WiredTiger files.

## Dependencies and Integration Points

Depends on `thread.h`, `load`, `testutil_verify`, WiredTiger thread wrappers, random helpers, and global connection `conn`.

## Risks and Edge Cases

The throughput calculation multiplies `(readers + writers) * total_nops`, although `total_nops` already sums thread operations, which may overstate ops/sec. Concurrent remove of absent keys tolerates `WT_NOTFOUND`.

## Test Signals

Signals are all threads start/stop, no unexpected cursor errors, final verify succeeds, and per-thread read/remove/update counts are printed.
