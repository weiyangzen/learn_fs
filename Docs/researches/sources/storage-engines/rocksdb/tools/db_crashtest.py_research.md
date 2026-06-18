<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest.py -->
# sources/storage-engines/rocksdb/tools/db_crashtest.py

## Purpose
`db_crashtest.py` orchestrates repeated `db_stress` runs for RocksDB crash consistency testing. It randomizes a very large option surface, sanitizes incompatible combinations, runs blackbox tests by externally terminating `db_stress`, runs whitebox tests with internal kill points and compaction-mode rotation, verifies final DB consistency, emits diagnostics, and cleans up DB and expected-value state after success.

## Important APIs, Types, and Functions
- Global option maps: `default_params`, `blackbox_default_params`, `whitebox_default_params`, `simple_default_params`, `cf_consistency_params`, `txn_params`, `optimistic_txn_params`, `best_efforts_recovery_params`, `blob_params`, `blob_direct_write_*_params`, `ts_params`, `tiered_params`, and `multiops_txn_params`.
- `early_argument_parsing_before_main()` parses seed overrides before global random defaults are evaluated and detects remote DB mode from `--env_uri` or `--fs_uri`.
- `apply_random_seed_per_iteration()` reseeds every run, preserving reproducibility when requested.
- `stress_cmd_env()` injects `TSAN_OPTIONS=suppressions=.../tsan_suppressions.txt` only when the caller has not already supplied TSAN settings.
- `get_db_parent_dir()`, `get_ev_parent_dir()`, and `setup_multiops_txn_key_spaces_file()` allocate DB, expected-value, and transaction key-space paths while respecting `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, and remote DB constraints.
- `is_direct_io_supported()` probes local direct I/O support before leaving direct I/O flags enabled.
- `finalize_and_sanitize()` evaluates callable random values and applies the core compatibility matrix across WAL, blob direct write, direct I/O, timestamps, transactions, remote compaction, user-defined indexes, multiscan, cache tiering, compaction styles, fault injection, and multi-DB mode.
- `gen_cmd_params()` merges defaults, selected modes, and parsed CLI overrides by documented priority.
- `gen_cmd()` creates the sorted `db_stress` command line, creates expected-value directories, and returns both command and finalized parameters.
- Diagnostic helpers include `human_readable_bytes()`, `output_matches_no_space()`, `collect_diagnostic_roots()`, `format_filesystem_usage()`, `collect_directory_usage()`, and `build_out_of_space_diagnostics()`.
- Process helpers include `execute_cmd()`, `strip_expected_sigterm_stderr()`, `cleanup_after_success()`, and `print_and_cleanup_fault_injection_log()`.
- Entrypoints are `blackbox_crash_main()`, `whitebox_crash_main()`, and `main()`.

## Control Flow
Module import immediately runs early seed parsing and initializes randomized defaults. `main()` builds an argparse parser from the union of known parameter maps, parses remaining arguments, validates local `TEST_TMPDIR`, optionally overrides `stress_cmd`, and dispatches by `test_type`.

In blackbox mode, the script builds a persistent DB and expected-values directory, loops until `duration`, reseeds every iteration, generates a sanitized command, starts `db_stress`, waits `interval`, terminates it on timeout, filters narrow expected post-SIGTERM io_uring stderr, fails on unexpected early exit or stderr, and resets `destroy_db_initially` after the first run. After the loop it runs one final `verification_only=1` pass with `skip_verifydb=0` and `verify_timeout`, then destroys the DB through `db_stress --destroy_db_and_exit`.

In whitebox mode, the script loops until `duration` and rotates `check_mode`: kill-point stress, universal compaction, FIFO compaction, and normal operation. Kill mode also rotates through different `kill_exclude_prefixes` and odds to hit different write-path regions. When compaction style changes after the halfway mark, it sets `destroy_db_initially=1` to avoid reusing incompatible DB state. Each run must either die as expected when kill testing or return zero in non-kill runs. Completion or timeout triggers cleanup.

## State and Persistence Behavior
Persistent state is split between the RocksDB DB path and local expected-values state. The DB path may use a local or remote Env and is created/destroyed by C++ `db_stress`; expected values are always managed by Python on the local filesystem. Multi-DB mode creates `db_0`, `db_1`, etc. under the expected-values parent. The script stores global `ev_parent_dir_global` and `multiops_txn_key_spaces_file` so temporary artifacts can be removed at the end. Fault-injection logs are discovered in `TEST_TMPDIR` or `/tmp` by PID and printed in bounded tail form.

## Dependencies and Integration Points
The main external binary is `./db_stress`, configurable via `--stress_cmd`. Cleanup also uses that binary with `--destroy_db_and_exit=1` so it uses the same RocksDB Env and URI flags. The script relies on Python stdlib modules only, but it is tightly coupled to the `db_stress` flag set and RocksDB feature compatibility. It integrates with TSAN suppressions, `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, `DEBUG_LEVEL`, optional `pstack`, remote filesystem flags, and Linux direct-I/O behavior.

## Risks and Edge Cases
- The compatibility matrix is large and order-sensitive. Later sanitizers can override earlier command-line choices, so adding a new feature flag requires reasoning about every interacting mode.
- Import-time randomization means tests that import this module must control `sys.argv` and seeds before execution.
- Blackbox mode treats timeout as expected, but unexpected stderr after SIGTERM fails unless filtered by `_IGNORED_SIGTERM_STDERR_RE`. The filter is deliberately narrow to avoid hiding real io_uring failures.
- Remote DB mode disables features whose local-file visibility assumptions do not hold, especially blob direct write and direct I/O.
- `gen_cmd()` sorts flags for reproducibility, but unknown args pass through unsanitized.
- Out-of-space diagnostics parse absolute paths from output. This is useful in CI but can be expensive on very large directory trees.
- `whitebox_crash_main()` treats long timeout as acceptable cleanup territory, so callers must inspect surrounding output for hangs versus true success.

## Test Signals
The companion `db_crashtest_test.py` unit tests exercise TSAN environment handling, expected-values directory preservation, sanitization for WAL-disabled, blob direct write, range-conversion, and multi-DB modes, SIGTERM stderr filtering, no-space detection, suffix accounting, and out-of-space diagnostics. The broader integration signal is successful blackbox or whitebox crash-test execution with final verification and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest.py -->
