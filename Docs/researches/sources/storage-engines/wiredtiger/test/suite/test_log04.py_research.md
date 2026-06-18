# sources/storage-engines/wiredtiger/test/suite/test_log04.py

## Purpose
Smoke-tests interactions among logging, timestamps, non-logged objects, checkpoints, and rollback to stable.

## APIs, Types, And Functions
Defines `test_log04` with logged connection config, row/column scenarios, and checkpoint/no-checkpoint scenarios. It uses `SimpleDataSet`, `Connection.set_timestamp`, transaction commit timestamps, read timestamp checks, optional `Session.checkpoint`, and `Connection.rollback_to_stable`.

## Control Flow, State, And Persistence
The test creates one logged table, one non-logged timestamped table, and one non-logged table updated without timestamps. It verifies initial data, rolls back an uncommitted update, commits at timestamps 20 and 30, advances stable to 25, optionally checkpoints, and runs rollback to stable. Logged and non-timestamped tables ignore timestamp rollback, while non-logged timestamped data rolls back the timestamp-30 update.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp hook prevention, logging enabled at connection level, per-object `log=(enabled=false)`, and RTS. Risks are applying timestamps to logged data or failing to roll back non-logged timestamped data. Signals are read-timestamp value assertions before and after rollback to stable.
