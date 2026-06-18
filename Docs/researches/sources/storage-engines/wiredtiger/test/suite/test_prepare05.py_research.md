# sources/storage-engines/wiredtiger/test/suite/test_prepare05.py

## Purpose
Validates timestamp ordering rules for prepare, commit, and durable timestamps.

## APIs, Types, And Functions
Defines `test_prepare05` with column and row-integer scenarios. It uses `Connection.set_timestamp`, `Session.prepare_transaction`, `Session.timestamp_transaction`, cursor writes, and error-message assertions.

## Control Flow, State, And Persistence
The test creates a table, sets stable timestamp 2, then verifies prepare timestamp 1 and 2 are rejected because they are not newer than stable. It confirms prepare timestamp 3 can be committed with matching commit/durable timestamps. It then verifies setting commit timestamp before prepare is illegal, including when prepare timestamp is already set through `timestamp_transaction`. Finally it confirms a transaction with write data can commit with commit and durable timestamps equal to the prepare timestamp.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepared timestamp validation and timestamp API state ordering. Risks are accepting prepare timestamps at or before stable, or allowing commit timestamp before prepare. Signals are exact error messages and successful legal commit cases.
