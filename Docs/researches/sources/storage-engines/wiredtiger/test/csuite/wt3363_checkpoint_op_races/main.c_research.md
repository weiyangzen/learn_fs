# sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/main.c

## Purpose
WT-3363 detects operations that block unexpectedly behind a slow checkpoint. It runs repeated delayed checkpoints alongside worker threads issuing create/drop/bulk/cursor operations and aborts if any worker stops making progress for too long.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `TEST_PER_THREAD_OPTS`, `pthread_create/join`, `WT_EVENT_HANDLER`, `WT_RAND_STATE`, and shared operation helpers such as `op_bulk`, `op_create`, `op_cursor`, `op_drop`, `op_bulk_unique`, and `op_create_unique`.
- Connection config enables `timing_stress_for_test=[checkpoint_slow]`.
- `do_checkpoints` runs forced checkpoints and tolerates `EBUSY`/`ENOENT`.
- `do_ops` randomly chooses one of six operations.
- `monitor` samples per-thread operation counters and aborts if a counter is unchanged over half the checkpoint delay.

## Control Flow
The test exits immediately unless `TESTUTIL_ENABLE_TIMING_TESTS` is set because runtime is 15 minutes. When enabled, it opens a 1 GiB-cache database with timing stress, starts one checkpoint thread, ten operation threads, and one monitor thread. All threads run until `RUNTIME` elapses. Main joins operation, monitor, and checkpoint threads, prints success, and cleans up.

## State and Persistence Behavior
The workload creates and drops objects and may optionally populate data depending on test options. Persistence is incidental; the key state is per-thread progress counters plus database metadata/object handles under checkpoint contention.

## Dependencies and Integration Points
The file depends on test operation helpers defined elsewhere in the same csuite test target and on timing-stress support. It integrates with smoke wrapper variants with and without `-d`.

## Risks and Test Signals
The primary signal is an abort from `monitor`, preserving a core for blocked-operation diagnosis. Long runtime and timing dependence make it sensitive to slow machines. The counter array initialization uses `memset(last_ops, 0, sizeof(int) + N_THREADS)`, which appears smaller than the array and is a maintenance risk, though stack values are overwritten as counters advance.
