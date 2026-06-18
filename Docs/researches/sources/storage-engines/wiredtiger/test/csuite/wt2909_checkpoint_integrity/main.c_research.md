# sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/main.c

## Purpose
WT-2909 tests checkpoint integrity under injected filesystem write failures. A child process populates two related tables through the `fail_fs` extension, failures are injected around checkpointing, and the parent reopens the home with the normal filesystem to verify recovery and data/index consistency.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `WT_CURSOR`, `WT_SESSION`, `WT_EVENT_HANDLER`, `WT_RAND_STATE`, `fork`, `execv`, `waitpid`, `setenv`, `freopen`, and `setrlimit`.
- `check_results` opens recovered tables and indices, walks both main tables in lockstep, and verifies all secondary indexes.
- `generate_key`, `generate_value`, and `create_big_string` provide deterministic expected data from record number and stored random integer.
- `enable_failures` and `disable_failures` configure `WT_FAIL_FS_ENABLE`, `WT_FAIL_FS_WRITE_ALLOW`, and `WT_FAIL_FS_READ_ALLOW`.
- `run_check_subtest_range` binary-searches the number of allowed writes where recovery crosses from too-early failure to checkpoint-success behavior.
- `subtest_main` loads `WT_FAIL_FS_LIB` with `early_load` and `environment=true`; `subtest_populate` performs transactional writes and targeted checkpoint failure injection.

## Control Flow
The top-level `main` parses options, defaults to 50,000 records, and either dispatches a `subtest`/`subtest_close` child mode or runs parent orchestration. Parent mode calibrates the failure threshold unless `-o` supplies a fixed allowed-write count, then runs both early-exit and close-after-failure child variants. Each child creates `table:subtest`, `table:subtest2`, and three indexes, writes matching records in transactions, takes an initial checkpoint after the first insert, enables failure injection near 1% of the workload, and attempts a checkpoint. The parent removes/recreates homes between subtests and always verifies recovered content afterward.

## State and Persistence Behavior
Persistent state includes two tables, one indexed table, secondary indexes, log files, stdout/stderr files in the home, and possibly a partially written checkpoint. Transactions keep the two tables synchronized. Recovery must leave a prefix of records where both tables and all indexes agree. `subtest_close` intentionally tests cleanup/close after an expected filesystem failure; normal subtest exits immediately after expected failure.

## Dependencies and Integration Points
The test depends on Unix process APIs and does not run on Windows. It requires the `fail_fs` extension shared library and build-directory discovery via `-b`/`testutil_build_dir`. It integrates with csuite row/column variants through `-t r` and `-t c`.

## Risks and Test Signals
Hard failures include unrecoverable homes, missing tables, table count mismatch, index count mismatch, wrong values, unexpected child failures, or inability to calibrate the threshold after retries. Calibration is approximate and nondeterministic, so the harness treats missing both success/failure sides as `EAGAIN` and retries. One call in fixed-`-o` mode passes `opts->nrecords` as the `close_test` boolean, effectively always true for nonzero records; that is a noteworthy maintenance risk.
