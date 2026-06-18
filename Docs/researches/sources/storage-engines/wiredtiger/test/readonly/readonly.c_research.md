# sources/storage-engines/wiredtiger/test/readonly/readonly.c

Purpose: integration test for WiredTiger readonly connection semantics, lock-file behavior, read/write reopen restrictions, and data visibility from read-only homes.

Important APIs and control flow: parent mode creates a table `table:main`, inserts `MAX_KV` large values, copies the home into writable/no-lock and chmod-readonly variants, then opens four parent connections and invokes fresh child processes with `-R` or `-W`. Child mode calls `open_dbs()`, which runs `run_child()` against each directory with expected success or failure. `run_child()` opens with readonly or writable config, scans the table, and asserts exactly `MAX_KV` rows.

State and persistence behavior: creates `WT_RD`, `WT_RD.WRNOLOCK`, `WT_RD.RD`, and `WT_RD.RDNOLOCK`, copies database files, removes selected `WiredTiger.lock` files, changes permissions to read-only, and restores permissions for cleanup. WiredTiger state includes logs, statistics, statistics log output, and the table data.

Dependencies and integration points: depends on `test_util.h`, POSIX `system`, `chmod`, process exit status macros, file-copy helpers, and WiredTiger open/session/cursor APIs. `smoke.sh` wraps it and installs a chmod cleanup trap.

Risks: permission behavior is platform and filesystem dependent. Child execution uses `system()` and command string formatting, so paths with shell-sensitive characters would be risky. The test expects several WiredTiger error messages and must not treat them as failures.

Test signals: child process exit status validates each scenario; row-count scans validate read visibility; final output prints `Readonly test successful`.
