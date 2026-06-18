# sources/storage-engines/wiredtiger/test/suite/test_txn02.py

## Purpose
`test_txn02.py` is a scenario matrix for transaction operations, visibility, and logged recovery across multiple operations and commit/rollback choices.

## Important APIs, Types, and Functions
The class `test_txn02` inherits `WiredTigerTestCase` and `suite_subprocess`. It defines scenario lists for table type, up to four operations, and commit/rollback outcomes, with helpers `conn_config`, `check`, `check_all`, `check_log`, and `test_ops`.

## Control Flow
Each scenario creates a table, performs a sequence of writes/truncates/removes inside transactions, updates expected current and committed dictionaries according to commit/rollback, checks visibility from different isolation levels, then uses a copied/recovered home or log inspection path to verify committed state after recovery.

## State and Persistence Behavior
The test exercises logged table state and transaction state transitions. Only committed operations should survive checkpoints, recovery, and backup-style reads.

## Dependencies and Integration Points
Depends on `suite_subprocess`, `runWt`/log tooling, filesystem log files, `make_scenarios`, and WiredTiger transaction isolation.

## Risks and Edge Cases
The matrix is pruned because the Cartesian product is large. Risk clusters include incorrect rollback of range operations, read-uncommitted visibility errors, and mismatched log replay.

## Test Signals
Dictionary comparisons in `check_all` and recovery/log checks must match the scenario's expected committed state.
