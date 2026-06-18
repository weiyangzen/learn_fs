# sources/storage-engines/wiredtiger/test/manydbs/manydbs.c

Purpose: stress test for multiple simultaneous WiredTiger connections and condition-variable wake/reset behavior under idle and light write workloads.

Important APIs and functions: `get_stat` opens a `statistics:` cursor and reads selected connection stats. `run_ops` writes random-sized byte values to random databases. `main` parses `-D maxdbs`, `-h dir`, and `-I` idle mode; creates per-database homes; opens up to `dbs` connections rotating transaction sync configs; optionally creates `table:main`; records `WT_STAT_CONN_COND_AUTO_WAIT_RESET`; sleeps and optionally writes over 30 seconds; then checks reset thresholds.

Control flow and state: arrays track connections, sessions, cursors, and baseline reset counts. Each database lives under `WT_TEST/WT_TEST.<i>`. In idle mode cursors are not allocated and no table is created. Non-idle mode writes to a quarter of databases per cycle.

Dependencies and integration: uses `test_util.h`, WiredTiger public APIs, internal random helpers, and stat IDs. CMake registers it as `test_manydbs`.

Risks and test signals: thresholds are platform-specific for spurious condition-variable wakeups, with looser allowances on NetBSD, Windows, and macOS. The test intentionally has wall-clock sleeps and can be timing-sensitive. Strong signals are no idle resets beyond threshold and resets under light workload staying below a fraction of waits.
