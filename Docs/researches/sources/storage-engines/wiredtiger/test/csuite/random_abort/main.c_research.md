# sources/storage-engines/wiredtiger/test/csuite/random_abort/main.c

Purpose: crash/recovery stress test that forks a writer process, lets multiple threads write row-store and column-store tables plus sidecar record logs, kills the child with `SIGKILL`, runs WiredTiger recovery, and verifies that recovered records are consistent with the durable prefix described by the sidecar files.

Important APIs, types, and functions: global options control compatibility mode, compaction, in-memory logging, and LazyFS. `thread_run` writes records forever, alternating row/column tables by thread ID, performing inserts, removes, and modify/update operations, and logging inserted/deleted/modified keys to per-thread files under `RECORDS_DIR`. `fill_db` creates `table:main` and `table:col_main`, opens the connection with log/transaction_sync config, and starts writer threads. `recover_and_verify` reopens with recovery config, reads sidecar files, and validates key presence/absence/value contents. `handler` cleans up LazyFS if the child exits unexpectedly.

Control flow: `main` parses options (`-C`, `-c`, `-h`, `-l`, `-m`, `-p`, `-T`, `-t`, `-v`), chooses random or fixed thread counts and timeout, creates the work directories and LazyFS if enabled, forks the child to run `fill_db`, waits until every worker has created its three record files, sleeps the timeout, kills the child, copies data for debugging, optionally clears LazyFS cache, changes into the home, and runs recovery verification. Verify-only mode skips the fork and requires an explicit thread count.

State and persistence behavior: creates `WT_TEST.random-abort` or `WT_TEST.random-abort-lazyfs`, a nested `WT_HOME`, record files for inserts/deletes/modifies, debug data copies, optional LazyFS backing/cache state, log files, and row/column tables. It cleans artifacts unless preservation or failure prevents cleanup.

Dependencies and integration points: depends on POSIX fork/signals/wait, WiredTiger logging/recovery, transaction sync variants, `wiredtiger_calc_modify`, column-store record numbering, LazyFS test utilities, `testutil_copy_data`, and smoke scripts that run disk, in-memory, compatibility, and LazyFS variants.

Risks: sidecar files can contain partial lines after `SIGKILL`; verification explicitly treats malformed/partial tails as EOF. The test assumes recovered durable data forms a prefix per thread; any later existing key after a missing key is fatal. LazyFS mode changes durability expectations by clearing the cache. Workload threads never stop voluntarily, so process control must be correct.

Test signals: successful recovery prints the number of verified records and exits zero. Non-in-memory runs fail if records that should be durable are absent or values mismatch. Smoke scripts exercise fixed five-thread, fixed-time variants across compatibility, in-memory, and LazyFS modes.
