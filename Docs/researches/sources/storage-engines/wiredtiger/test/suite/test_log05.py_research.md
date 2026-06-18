# sources/storage-engines/wiredtiger/test/suite/test_log05.py

## Purpose
Regression test for recovery from oversized corrupted log record lengths without generating duplicate log files.

## APIs, Types, And Functions
Defines `test_log05` with logging enabled. Helpers parse `checkpoint_lsn` from `WiredTiger.turtle`, seek into `WiredTigerLog.0000000%03d`, and overwrite the record length with `UINT32_MAX` using `struct.pack`. It uses `WiredTigerCursor` and expected stdout matching.

## Control Flow, State, And Persistence
The test creates data in one transaction, then repeats 20 cycles: close the connection, corrupt the next log file at the checkpoint LSN, and reopen expecting a corrupted-length recovery message. After the cycles, it counts existing log files and asserts no more than two remain. Recovery should salvage and continue rather than proliferating log files.

## Dependencies, Integration, Risks, And Test Signals
Depends on turtle file format, log naming, little-endian record length, and recovery salvage. Risks are brittle offsets if metadata format changes, failed recovery, or disk growth from duplicate logs. Signals are expected stdout pattern and final log count bound.
