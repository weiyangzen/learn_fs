# sources/sync-backup/git-lfs/t/cmd/lfstest-count-tests.go

Purpose: coordinates integration-test server lifetime by maintaining a shared active-test count.

Important APIs/functions: `countFn`, `main`, `acquire`, `release`, `callWithCount`, `path`, and `fatal`.

Control flow: acquires an exclusive lock file with a 5 second timeout. With no args it prints the current count. `increment` starts `lfstest-gitserver` when transitioning from zero to one and increments otherwise. `decrement` decrements while count remains above one, or posts `/shutdown` to the server and writes zero when the last test exits.

State/persistence behavior: stores `test_count` and `test_count.lock` adjacent to `LFSTEST_DIR`, creates `gitserver.log`, starts a background server process, and reads `LFS_URL_FILE` for shutdown.

Dependencies/integration: invoked by shell test setup/teardown to share one server across parallel tests.

Risks: stale lock files can block for the timeout. `fatal` attempts release even when acquire may have failed. Shutdown POST ignores errors after reading URL.

Test signals: count file values, server process/log existence, and successful shutdown when count reaches zero.
