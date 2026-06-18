# sources/storage-engines/wiredtiger/test/suite/test_timestamp08.py

## Purpose
`test_timestamp08.py` tests the integer timestamp API variants, read timestamp behavior, oldest-reader queries, and all-durable timestamp calculation.

## Important APIs, Types, and Functions
The class uses `session.timestamp_transaction_uint` with `WT_TS_TXN_TYPE_COMMIT`, `READ`, `PREPARE`, and `DURABLE`; `conn.query_timestamp`; `conn.set_timestamp`; `prepare_transaction`; and `standalone_build` conditional error expectations.

## Control Flow
`test_timestamp_api` validates zero timestamp rejection, first-commit ordering, oldest/stable constraints, non-monotonic commits across separate transactions, read timestamp rejection below oldest, read visibility at timestamps 7 and 8, `oldest_reader` results, and forced backward oldest movement. `test_all_durable` checks all-durable before first commit, after commits, while lower-timestamp transactions are running, across prepared transactions with durable timestamps, with multiple commit timestamps in one transaction, and after checkpoint/reopen.

## State and Persistence Behavior
The table stores timestamped records and prepared transaction metadata. Connection timestamp state and running transaction state affect `oldest_reader` and `all_durable`. Checkpoint/reopen verifies checkpoint timestamp survives recovery.

## Dependencies and Integration Points
It integrates Python integer timestamp bindings with transaction, prepare, checkpoint, recovery, and timestamp query APIs.

## Risks and Test Signals
Risks include divergence between string and integer timestamp APIs and incorrect all-durable minima. Signals are expected errors, point read visibility, and exact queried timestamp values.
