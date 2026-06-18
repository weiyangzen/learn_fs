# sources/storage-engines/wiredtiger/test/suite/test_prepare07.py

## Purpose
Ensures an active prepared transaction older than oldest timestamp does not make its update visible in backups after oldest/stable advance.

## APIs, Types, And Functions
Defines `test_prepare07` with column and string-row scenarios. It uses `SimpleDataSet`, timestamped transactions, a separate prepared session, `Connection.set_timestamp`, `Session.checkpoint`, `backup`, `wiredtiger_open` on the backup, and cursor reads.

## Control Flow, State, And Persistence
The test populates base rows, inserts many large values, checkpoints, then commits updates at timestamps 110 and 120, prepares an update at 130 and leaves it open, commits more updates at 140 and 150, advances stable and oldest to 155, commits another update at 160, and checkpoints before resolving the prepared transaction with commit timestamp 140 and durable timestamp 160. A backup is taken and opened. The backup must include stable non-prepared updates, exclude the prepared update because it was not durable at checkpoint, and exclude the timestamp-160 update newer than stable.

## Dependencies, Integration, Risks, And Test Signals
Depends on backup, checkpoint visibility, prepared durable timestamp handling, and `txn_visible_all` behavior when oldest advances past a prepared transaction. Risks are visibility gaps that expose prepared updates or newer-than-stable data. Signals are exact value checks in the backup for keys nrows+1 through nrows+6.
