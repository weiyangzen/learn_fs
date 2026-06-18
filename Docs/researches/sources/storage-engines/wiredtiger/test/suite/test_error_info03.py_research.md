# sources/storage-engines/wiredtiger/test/suite/test_error_info03.py

## Purpose

Covers `get_last_error()` details for `EBUSY` drop failures caused by specific locks, backup cursors, data handles, uncommitted data, and dirty data.

## Important APIs, Types, and Functions

`test_error_info03` inherits `error_info_util`, configures timing stress, and defines lock-holder helpers, drop helpers, and tests for checkpoint, schema, table, backup, dhandle, uncommitted, and dirty conflicts.

## Control Flow

The lock tests start threads that hold locks through `session.alter` or index/table cursor activity, then concurrently attempt `drop(..., lock_wait=0...)`. Backup and dhandle tests keep a backup cursor or object cursor open. Transactional tests use uncommitted or recently committed data before drop.

## State and Persistence Behavior

State includes live threads, held locks, backup cursor handles, open data handles, and transactional dirty/uncommitted content. The test relies on timing stress settings and sleeps to place operations in the intended lock windows.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wtthread`, `time`, `errno`, `wttest`, `open_cursor`, and `error_info_util`. It is skipped for disaggregated mode because `Session.alter` is unsupported.

## Risks and Maintenance Signals

Thread scheduling and timing-stress points are central; changes to schema lock acquisition order can alter the observed sub-reason. Some cursors are intentionally kept open until after assertions.

## Test Signals

Signals are `errno.EBUSY` plus exact sub-reasons for checkpoint lock, schema lock, table lock, backup, dhandle, uncommitted data, and dirty data.
