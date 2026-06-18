
# sources/user-network-fs/rclone/fstest/test_all/test_all.go

Purpose: command `test_all` is rclone's integration-test runner across configured remotes and packages.

Important APIs/types/functions: global `Opt *runs.RunOpt` is populated by flags in `init`. `main` loads config, filters by requested remotes/backends/tests, optionally cleans, builds test binaries, runs tests concurrently, records results, and emits reports.

Control flow: after flag parsing and config install, CSV parsing handles remote names with commas. Test runs are shuffled, a `runs.Report` is created, one binary per package is built unless disabled, and goroutines execute `run.Run` behind a token dispenser bounded by `-n`. Results are gathered, summarized, written to JSON/HTML, optionally emailed/uploaded, and nonzero exit is used if any run failed.

State/persistence: writes report/log output under `-output`, may build/delete test binaries in source directories, sets `RCLONE_CACHE_DB_WAIT_TIME`, starts test servers, and registers `testserver.CleanupAll` with `atexit`.

Dependencies/integration: imports all backends, configfile installer, `runs`, `testserver`, `atexit`, and `pacer`.

Risks: high concurrency can stress remote APIs or local Docker. `LogHTML` browser opening is inherited from report generation. Interrupt handling depends on `atexit` to stop test servers.

Test signals: exit status plus generated report files are the primary signals. Per-run logs preserve exact command output for triage.
