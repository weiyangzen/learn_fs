# sources/storage-engines/wiredtiger/test/suite/test_truncate26.py

## Purpose
`test_truncate26.py` checks session ownership validation for truncate cursors: start and stop cursors must belong to the same session that issues `truncate`.

## Important APIs, Types, and Functions
The file defines `test_cursor24(wttest.WiredTigerTestCase)` with `test_cursor24_truncate`. It uses `SimpleDataSet`, two sessions, start/stop cursors opened in different sessions, `session.truncate`, and `assertRaisesWithMessage`.

## Control Flow
After populating a small table, the test opens start/stop cursors from the primary session and from a second session. A truncate with both second-session cursors succeeds. Three mixed-cursor combinations are then attempted from the second session and are expected to fail.

## State and Persistence Behavior
Persistence is minimal; the table is a small validation fixture. The persistent data is less important than the API contract that cursor handles carry session ownership.

## Dependencies and Integration Points
Depends on WiredTiger cursor/session handle validation and the Python test harness error assertion helper.

## Risks and Edge Cases
The risk is accepting a cursor from another session, which can corrupt transaction context, locking, or cursor lifecycle assumptions. Both mixed-start and mixed-stop cases are covered.

## Test Signals
One valid truncate returns 0, and each mixed-session call raises `WiredTigerError` with a message matching "same session".
