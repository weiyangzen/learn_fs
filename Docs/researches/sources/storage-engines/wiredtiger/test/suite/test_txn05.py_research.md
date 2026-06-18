# sources/storage-engines/wiredtiger/test/suite/test_txn05.py

## Purpose
`test_txn05.py` checks logged transaction behavior for a scenario set of operations and commit/rollback decisions, with explicit validation of log replay.

## Important APIs, Types, and Functions
The class defines `conn_config`, `check`, `check_all`, `check_log`, and `test_ops`. It uses small log files, disabled log removal, `transaction_sync`, `suite_subprocess`, log file enumeration, and recovery-style validation.

## Control Flow
The test creates a table, performs the scenario operation inside a transaction, checks visible current and committed states under isolation levels, resolves the transaction, forces/log-checks persistence, and validates committed state through log/recovery inspection.

## State and Persistence Behavior
Logged records in `WiredTigerLog.*` are central. Rollbacks must not produce recovered updates, while commits must survive log replay.

## Dependencies and Integration Points
Depends on Python `fnmatch`, `os`, `time`, the suite subprocess harness, `make_scenarios`, and WiredTiger log configuration.

## Risks and Edge Cases
Small log files and operation matrices stress log rotation, transaction sync, and rollback records. Scenario pruning avoids very long combinations.

## Test Signals
Expected dictionaries from `check_all` and `check_log` must align with the committed state.
