# sources/storage-engines/wiredtiger/bench/tiered/push_pull.c

## Purpose
This benchmark measures tiered-storage checkpoint push/pull behavior for different logical table sizes, comparing checkpoint with and without `flush_tier`, and validating recovered data.

## Important APIs, Types, and Functions
Key functions are `main`, `run_test_clean`, `run_test`, `populate`, `recover_validate`, `get_file_size`, `compute_tiered_file_size`, `compute_wt_file_size`, `fill_random_data`, `difftime_msecs`, `difftime_sec`, and `calculate_std_deviation`. It uses `TEST_OPTS`, `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, `WT_ITEM`, WiredTiger random helpers, and test utility filesystem functions.

## Control Flow
`main` parses test options and runs each size twice: first without flush, then with flush enabled when tiered storage is active. `run_test_clean` repeats each size `MAX_RUN` times, cleaning homes and averaging write/read time, throughput, file size, and standard deviation. `run_test` opens a home, creates a table, populates deterministic random records, checkpoints with optional `flush_tier`, computes file size after close, and optionally calls `recover_validate`. Recovery reopens the home, regenerates the same random sequence, scans all records, and verifies keys and values.

## State, Persistence, and Dependencies
Persistent state is per-run WiredTiger homes, local `.wt` files or tiered `.wtobj` files, copied debug data, and table contents. Dependencies include tiered-storage test options, directory-store support, POSIX stat/getcwd/chdir, math library, and WiredTiger test utilities.

## Integration Points, Risks, and Test Signals
It integrates table population, checkpoint, tiered flush, recovery, file-size accounting, and throughput reporting. Signals are assertions during recovery and printed averages. Risks include fixed `MAX_TIERED_FILES`, sleep-based file visibility, global arrays reused per run, and dependence on deterministic random seeding.
