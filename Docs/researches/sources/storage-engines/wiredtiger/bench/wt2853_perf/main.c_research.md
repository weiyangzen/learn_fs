# sources/storage-engines/wiredtiger/bench/wt2853_perf/main.c

## Purpose
`main.c` is a standalone WT-2853 performance regression workload. It creates a table with multiple indices, runs concurrent insert/update and read/index traversal threads, detects long progress gaps, and writes a small performance JSON summary.

## Important APIs, Types, and Functions
Important types are `SHARED_OPTS` for index URIs and row/column mode and `THREAD_ARGS` for per-thread arguments and counters. Key functions are `main`, `thread_insert`, `thread_get`, and `create_perf_json`. Constants define record counts, insert count, thread counts, gap warning threshold, and 1KB payload.

## Control Flow
`main` parses test options, recreates the home, opens WiredTiger with statistics logging, creates the table and `post`, `bal`, and `flag` indices, inserts one seed row, starts insert and get threads, waits for inserts, signals readers to stop, prints counts/warnings, writes JSON, and cleans up. Insert threads repeatedly choose random keys, begin a transaction, set indexed values, insert/update rows, handle `WT_ROLLBACK`, commit, and report elapsed gaps. Get threads repeatedly begin a transaction, search the `post` index, walk matching entries, validate invariants against both index and primary table reads, reset cursors, rollback, and record long gaps.

## State and Persistence Behavior
The test persists a WiredTiger home during execution, statistics logs through WT config, and `wt2853_perf.json` with metrics for cursor joins and gap warnings. Table/index contents are temporary and cleaned by `testutil_cleanup`.

## Dependencies and Integration Points
It uses `test_util.h`, WiredTiger sessions/cursors/transactions, pthreads, and WiredTiger internal random/time helpers. It is built by the local CMake file and exercised by `smoke.sh` in row and column-store modes.

## Risks and Edge Cases
The test is performance-sensitive and explicitly allows gap warnings on slow hosts. `done` is a plain int shared between threads without atomic/locking, which is typical for this test but data-racy in strict terms. It treats insert conflicts as acceptable rollback, but other errors assert. Runtime is sizable (`N_INSERT` is one million), so smoke execution can be expensive.

## Test Signals
Primary signals are successful completion, nonzero cursor join count, low or zero gap warnings, and valid `wt2853_perf.json`. Running both `-t r` and `-t c` covers row and column table key paths.
