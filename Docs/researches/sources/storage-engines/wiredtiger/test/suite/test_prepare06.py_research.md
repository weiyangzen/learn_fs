# sources/storage-engines/wiredtiger/test/suite/test_prepare06.py

## Purpose
Tests `roundup_timestamps=(prepared=true)` behavior for prepared transactions whose supplied timestamps are older than stable or oldest timestamps.

## APIs, Types, And Functions
Defines `test_prepare06` with column and row-integer scenarios. It uses `Connection.set_timestamp`, `Session.begin_transaction` with roundup config, `prepare_transaction`, `timestamp_transaction`, and commit.

## Control Flow, State, And Persistence
The test sets oldest timestamp 20 and stable timestamp 30, first confirms a prepare timestamp 10 is rejected without roundup. It then begins transactions with prepared timestamp rounding enabled and supplies prepare/commit timestamps earlier than stable and even earlier than oldest, while durable timestamp is 35. Both rounded prepared transactions must commit successfully.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp rounding rules for prepared transactions. Risks are rejecting legal rounded transactions or failing to round prepare/commit timestamps consistently. Signals are the initial expected rejection and successful commits for both roundup cases.
