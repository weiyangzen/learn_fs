# sources/storage-engines/wiredtiger/test/csuite/wt4333_handle_locks/main.c

## Purpose
WT-4333 stress-tests data handle locking, cursor caching, verification, checkpoint handles, and file-manager sweeping under concurrent opens, reads, writes, and verifies.

## Important APIs, Types, and Functions
- Global state tracks `WT_CONNECTION *conn`, worker/verify counters, busy counters, URI list, home path, and `done`.
- `uri_init` creates up to 750 tables and loads 10,000 string keys per table, then checkpoints.
- `op` opens a random URI, sometimes at `checkpoint=WiredTigerCheckpoint`, performs read or write scans, and sometimes caches the cursor in a per-thread slot.
- `wthread` loops worker operations; `vthread` mixes operations with `session->verify`.
- `on_alarm` flips `done` after the run period.
- `sweep_stats` prints selected cursor/data-handle sweep statistics.
- `runone` configures file-manager aggressive close settings and runs worker/verify threads for 60 seconds.

## Control Flow
`main` skips on macOS and otherwise calls `run`. `run` parses local options, chooses a default home if needed, installs an alarm handler, and randomly selects five scenarios from a table covering different worker counts, URI counts, and cursor-cache settings. Each scenario recreates the home, opens WiredTiger, initializes data, launches workers plus one verifier, waits for the alarm-driven stop, reports counters, optionally prints sweep stats, and closes the connection.

## State and Persistence Behavior
Each scenario creates many tables with deterministic string key/value data and a checkpoint used for read-only checkpoint cursors. Runtime state includes cached cursors per thread and EBUSY retry counters. Unless `-p` is specified, the home is removed after all runs.

## Dependencies and Integration Points
The test relies on pthreads, signals, atomic counter helpers, statistics cursors, file manager configuration, checkpoint cursors, and verify. It uses custom command-line parsing instead of `TEST_OPTS`.

## Risks and Test Signals
Unexpected errors from cursor open/search/insert/verify fail the test. High `EBUSY` counters are informational. The test is time- and platform-sensitive, skipped on macOS due to historical hangs. It is stress-oriented and can be resource-heavy with 64 workers and hundreds of files.
