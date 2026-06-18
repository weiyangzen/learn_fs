# sources/storage-engines/wiredtiger/test/suite/test_txn21.py

## Purpose
`test_txn21.py` is a smoke test for transaction-level `operation_timeout_ms` configuration.

## Important APIs, Types, and Functions
The class defines `test_operation_timeout_txn`. It passes `operation_timeout_ms=2000` to `begin_transaction`, `rollback_transaction`, and `commit_transaction`.

## Control Flow
The test begins and rolls back a transaction with timeout configured at begin, begins another transaction and passes timeout to rollback, then begins a third transaction and passes timeout to commit.

## State and Persistence Behavior
No table data is created. State is limited to session transaction lifecycle and config parsing.

## Dependencies and Integration Points
Depends on WiredTiger transaction config parsing for begin, commit, and rollback.

## Risks and Edge Cases
This is smoke coverage only; it does not force an operation timeout. It protects against rejecting the option on any of the transaction entry points.

## Test Signals
All three transaction sequences complete without `WiredTigerError`.
