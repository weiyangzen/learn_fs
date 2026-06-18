# sources/storage-engines/wiredtiger/test/suite/test_truncate22.py

## Purpose
`test_truncate22.py` verifies that a full range truncate committed at a timestamp removes historical keys after restart/checkpoint and does not leave the first key visible.

## Important APIs, Types, and Functions
The test class uses `SimpleDataSet`, `make_scenarios` for row and column key formats, `timestamp_str`, `conn.set_timestamp`, `session.timestamp_transaction`, `session.truncate`, `session.checkpoint`, and `reopen_conn`.

## Control Flow
It pins oldest and stable timestamps at 1, populates 10,000 rows at commit timestamp 2, reopens, starts a transaction with commit timestamp 5, opens start and stop cursors at keys 1 and `nrows`, truncates that complete range, commits, advances stable timestamp to 10, checkpoints, then searches key 1.

## State and Persistence Behavior
The table's timestamped update chain is persisted across reopen and checkpoint. Stable timestamp advancement makes the truncate durable and checkpointable.

## Dependencies and Integration Points
Depends on WiredTiger timestamp semantics, `SimpleDataSet` key conversion, and the test harness reopen behavior.

## Risks and Edge Cases
The important edge is a range truncate spanning the entire populated dataset after an initial restart. A regression could leave a boundary key visible or fail under column-store key handling.

## Test Signals
The final signal is `assertNotEqual(cursor.search(), 0)` for key 1, proving the key is absent.
