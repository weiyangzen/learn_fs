# sources/storage-engines/wiredtiger/test/suite/test_txn16.py

## Purpose
`test_txn16.py` tests that repeatedly toggling a database between logging enabled and disabled does not keep generating or reusing incorrect old log files.

## Important APIs, Types, and Functions
The class defines `populate_table`, `run_toggle`, and `test_recovery`, with `conn_on`, `conn_off`, and logging-enabled `conn_config`. It uses `helper.copy_wiredtiger_home`, `wiredtiger_open`, `fnmatch` log enumeration, and manual log removal.

## Control Flow
The test populates three tables with occasional checkpoints, copies the home to simulate crash state, closes the original, then runs the toggle loop on both original and copy. Each loop opens with logging on, records log names, removes logs, opens with logging off, and checks generated log sets.

## State and Persistence Behavior
The persistent state includes checkpointed table files and log files in two home directories. Re-enabled logging must not collide with removed original logs or keep adding new names indefinitely.

## Dependencies and Integration Points
Depends on filesystem log handling, WiredTiger logging/no-logging configuration, and tiered-storage skip behavior.

## Risks and Edge Cases
Manual log deletion is intentionally invasive. The test is skipped for tiered storage.

## Test Signals
Current log sets must be disjoint from original logs and stable across repeated toggles.
