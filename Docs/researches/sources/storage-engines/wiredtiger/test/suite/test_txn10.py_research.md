# sources/storage-engines/wiredtiger/test/suite/test_txn10.py

## Purpose
`test_txn10.py` tests recovery correctness for file ID allocation so log records for a table created after restart are not applied to an earlier table.

## Important APIs, Types, and Functions
The class defines `test_recovery`, table URIs `t1` and `t2`, logging configuration with dsync transaction sync, `reopen_conn`, `simulate_crash_restart`, and cursor iteration assertions.

## Control Flow
It creates `t1`, cleanly reopens, creates `t2`, writes 10,000 rows to `t2`, simulates a crash restart, then scans `t2` for all expected rows and scans `t1` to ensure it remains empty.

## State and Persistence Behavior
The test uses logged metadata and data records across a clean restart followed by a crash recovery. File ID mapping must be durable and replay-safe.

## Dependencies and Integration Points
Depends on `helper.simulate_crash_restart`, `suite_subprocess`, and WiredTiger log recovery.

## Risks and Edge Cases
The bug class is metadata/file-ID reuse: recovery might associate `t2` log records with `t1`.

## Test Signals
`t2` contains exactly keys 0-9999 with values key+1, and `t1` contains zero records after recovery.
