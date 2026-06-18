# sources/storage-engines/wiredtiger/test/suite/test_prepare01.py

## Purpose
Tests basic prepared transaction visibility across isolation levels, checkpoints, and a read-timestamp-after-prepare warning.

## APIs, Types, And Functions
Defines `test_prepare01` with row/column and file/table scenarios, plus `test_prepare01_read_ts`. Helpers count cursor-visible records, create named checkpoints, check transactions under read-uncommitted, snapshot, and read-committed isolation, and compare committed versus total rows.

## Control Flow, State, And Persistence
`test_visibility` inserts 1000 rows in transactions, periodically checks visibility before preparing and committing, and confirms prepared but uncommitted rows are visible only to the owning cursor/read-uncommitted while checkpoints include committed rows. Final prepare/commit makes all rows visible. The second class prepares a transaction then attempts to set a read timestamp, expecting a silently ignored warning.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepare timestamps, durable/commit timestamps, checkpoint cursors, isolation semantics, and column-store phantom filtering. Risks are leaking prepared updates to snapshot/read-committed readers or checkpointing uncommitted prepared data. Signals are record counts per isolation/checkpoint and expected stderr for ignored read timestamp.
