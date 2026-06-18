# sources/storage-engines/wiredtiger/test/suite/test_util04.py

## Purpose
`test_util04.py` tests the `wt drop` command against a table created through the API.

## Important APIs, Types, and Functions
The class defines `test_drop_process`, uses `session.create`, `tableExists`, `runWt(['drop', ...])`, and `assertRaises` on `session.open_cursor`.

## Control Flow
It creates `table:test_util04.a`, asserts the table exists, runs `wt drop table:test_util04.a`, asserts the table no longer exists, and verifies opening a cursor raises `WiredTigerError`.

## State and Persistence Behavior
The test mutates schema metadata and removes the table object. The dropped table must not remain accessible through metadata or data files.

## Dependencies and Integration Points
Depends on the external `wt drop` utility and the test harness `tableExists` helper.

## Risks and Edge Cases
This is a simple process/API integration test; it does not cover force flags or dependent schema objects.

## Test Signals
Existence transitions from true to false, and cursor open fails after drop.
