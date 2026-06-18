# sources/storage-engines/wiredtiger/test/suite/test_txn11.py

## Purpose
`test_txn11.py` checks empty checkpoints and log removal, ensuring repeated checkpoints can advance beyond original log files and reopening with log removal disabled succeeds.

## Important APIs, Types, and Functions
The class defines dynamic `conn_config`, `run_checkpoints`, and `test_ops`. It uses `SimpleDataSet`, `fnmatch.filter` over `*gerLog*`, repeated `session.checkpoint`, and `reopen_conn`.

## Control Flow
The test populates a source table, records original log files, repeatedly checkpoints until current log files are disjoint from the originals or a 500-checkpoint cap is reached, then changes `remove` to false and reopens.

## State and Persistence Behavior
The state under test is log file lifecycle and checkpoint metadata. Empty checkpoints should permit old logs to be removed/retired without corrupting later opens.

## Dependencies and Integration Points
Depends on filesystem log enumeration, WiredTiger logging/checkpointing, and the test harness reopen path.

## Risks and Edge Cases
The loop can be timing-sensitive if log file retirement is delayed. It assumes log filenames match `*gerLog*`.

## Test Signals
No explicit final value assertion exists; success is reaching reopen without errors after checkpoint/log transitions.
