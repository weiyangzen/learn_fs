# sources/storage-engines/wiredtiger/test/suite/test_txn17.py

## Purpose
`test_txn17.py` validates API calls tagged as requiring or forbidding active transactions.

## Important APIs, Types, and Functions
The class defines `test_txn_api` and uses `timestamp_transaction`, `commit_transaction`, `rollback_transaction`, `begin_transaction`, `checkpoint`, `timestamp_str`, and `assertRaisesWithMessage`.

## Control Flow
It first verifies timestamp, commit, and rollback calls fail when no transaction is running. It then begins a transaction and verifies a nested begin is rejected. Finally, it begins another transaction and verifies checkpoint is rejected while the transaction is active.

## State and Persistence Behavior
No durable table state is created. The test focuses on session transaction state and API validation.

## Dependencies and Integration Points
Depends on WiredTiger session API state checks and precise error messages.

## Risks and Edge Cases
Message matching is strict enough to catch wording changes. The timestamp value uses a huge shift but should fail due to state before timestamp size matters.

## Test Signals
Each invalid call raises `WiredTigerError` matching "only permitted in a running transaction" or "not permitted in a running transaction".
