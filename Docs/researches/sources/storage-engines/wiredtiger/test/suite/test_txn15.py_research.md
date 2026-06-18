# sources/storage-engines/wiredtiger/test/suite/test_txn15.py

## Purpose
`test_txn15.py` validates transaction sync configuration precedence between connection defaults, begin-transaction settings, and commit-transaction settings.

## Important APIs, Types, and Functions
The class defines `conn_config`, `mkvalue`, `syncLevel`, and `test_sync_ops`. Scenarios cover key formats, connection sync enabled/method, begin `sync=` settings, and commit `sync=` settings. It uses `stat.conn.log_release_write_lsn` and `stat.conn.log_sync`.

## Control Flow
Illegal scenarios with both begin and commit sync overrides return early. Legal scenarios create a table, snapshot log write/sync stats, perform one transaction, snapshot stats again, compute expected sync level, and compare stats accordingly.

## State and Persistence Behavior
Persistent data is a committed table update, but the main observed state is logging statistics that indicate whether release code explicitly waited for write or sync.

## Dependencies and Integration Points
Depends on WiredTiger logging stats, transaction sync config parsing, and `skip_for_hook("disagg")`.

## Risks and Edge Cases
Background log worker threads can increment sync stats, so the test only requires sync changes when explicit sync is expected.

## Test Signals
Write LSN stat changes when write/sync is expected; it remains equal when no waiting should occur.
