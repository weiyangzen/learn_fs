# sources/storage-engines/wiredtiger/test/suite/test_sweep06.py

## Purpose
`test_sweep06.py` is a WiredTiger sweep-server regression test. It checks that table data handles are not incorrectly marked expired or closed while their underlying file data handles are active under heavy concurrent access.

## Important APIs, Types, and Functions
The main class is `test_sweep06`, a `wttest.WiredTigerTestCase` plus `suite_subprocess` test. It configures the connection with aggressive file-manager sweep settings, high `session_max`, and `verbose=(sweep:3)`. `make_scenarios` runs the case with cursor caching disabled and enabled. The helper `insert(i, start, rows)` opens an independent session and cursor per table, inserts rows in one transaction, and closes both handles.

## Control Flow
`test_dhandles` optionally enables cursor caching, creates 199 numbered table URIs, and then performs 99 rounds of concurrent inserts across all tables using `wtthread.Thread`. After all worker threads join, it reads `statistics:` and asserts both `stat.conn.dh_sweep_dead_close` and `stat.conn.dh_sweep_expired_close` remain zero.

## State and Persistence Behavior
The test creates many tables and durable row updates, but the observed state is the connection data-handle cache and sweep accounting rather than table contents. Transactions are committed per worker session so handles are repeatedly acquired and released under concurrency.

## Dependencies and Integration Points
It integrates with `wtthread.Thread`, `suite_subprocess`, `wiredtiger.stat`, WiredTiger session/cursor APIs, and the sweep verbose subsystem. It is skipped for the disaggregated hook because multi-threaded tests are incompatible there.

## Risks and Test Signals
The risk under test is an invalid pointer or premature data-handle sweep when table/file handle relationships overlap. The pass signal is strict: no dead or expired dhandle close statistics may increase after the workload.
