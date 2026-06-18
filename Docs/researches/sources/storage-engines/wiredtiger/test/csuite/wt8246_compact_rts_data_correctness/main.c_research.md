# sources/storage-engines/wiredtiger/test/csuite/wt8246_compact_rts_data_correctness/main.c

## Purpose
WT-8246 verifies data correctness when foreground or background compaction is interrupted and recovery performs rollback-to-stable. It tests row and column stores across foreground/background compact modes.

## Important APIs, Types, and Functions
- Uses `fork`, `SIGKILL`, sentinel `compact_started`, timestamped transactions, recovery open, and foreground/background `session->compact`.
- Connection config enables `timing_stress_for_test=[compact_slow]` and `debug_mode=(background_compact)`.
- `workload_compact` populates data, performs timestamped full-table updates at 20/30/40/50, pins stable at 30, removes records at 60, checkpoints, then starts compact.
- `check` reads all records at a supplied timestamp and validates the visible string value.
- `large_updates` retries `WT_ROLLBACK` up to `MAX_RETRIES`.

## Control Flow
`main` runs four combinations of row/column and foreground/background. Each parent forks a child. Child creates the table, sets oldest/stable to 10, loads 800,000 records, checkpoints, updates all records through values A/B/C/D at timestamps 20/30/40/50, verifies them, sets stable to 30, removes a third at timestamp 60, checkpoints, and starts compact with `free_space_target=1MB`. Parent waits for the sentinel, sleeps briefly, kills child, opens recovery, and verifies timestamp reads: value A at 20 and value B at 30, 40, and 50 due to stable timestamp 30.

## State and Persistence Behavior
Timestamp history and stable timestamp are the core persistent state. Recovery should roll back updates newer than stable and preserve stable-visible data after interrupted compact. Foreground mode creates the sentinel before compact; background mode creates it after enabling background compaction and waits to let service work start.

## Dependencies and Integration Points
The test depends on RTS, background compaction debug mode, timing stress, process control, and nontrivial table volume. It uses `TESTUTIL_ENV_CONFIG_REC` for recovery open.

## Risks and Test Signals
Any missing record or wrong value at checked timestamps indicates compact/RTS correctness failure. It is resource-heavy and timing-sensitive. `large_updates` keeps `retry_attempts` across all records rather than resetting per key, which may make repeated rollbacks more likely to trip the global retry assertion.
