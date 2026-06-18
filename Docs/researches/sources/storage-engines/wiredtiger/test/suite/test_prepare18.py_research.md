# sources/storage-engines/wiredtiger/test/suite/test_prepare18.py

## Purpose

Ensures prepared transactions reject operations on logged tables.

## Important APIs, Control Flow, and State

With connection logging enabled, the test populates a logged table through `SimpleDataSet`, commits one ordinary update, begins another transaction on the same key, and calls `prepare_transaction('prepare_timestamp=1')`. It expects `WiredTigerError` with the message that a prepared transaction cannot include a logged table.

## Dependencies, Risks, and Test Signals

Dependencies are logging configuration, `SimpleDataSet`, and `assertRaisesWithMessage`. The risk is allowing prepared semantics on logged objects, which conflicts with timestamped prepared transaction guarantees. The test signal is the exact error path rather than any persisted state.
