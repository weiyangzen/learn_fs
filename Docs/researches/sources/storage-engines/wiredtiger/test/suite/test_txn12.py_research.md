# sources/storage-engines/wiredtiger/test/suite/test_txn12.py

## Purpose
`test_txn12.py` verifies that a failed cursor-open configuration operation does not poison the active transaction and prevent commit.

## Important APIs, Types, and Functions
The class defines `test_txn12`, uses `session.open_cursor` with invalid `next_random=bar`, `assertRaisesWithMessage`, read-only and read/write transactions, and commit.

## Control Flow
It opens a read-only transaction, performs a harmless cursor `next`, attempts an invalid cursor open and expects a boolean-configuration error, then commits successfully. It repeats in a read/write transaction after inserting key 123.

## State and Persistence Behavior
The second transaction persists one table update if commit succeeds. The main state is the transaction error flag, which should not be set by this failed open-cursor validation.

## Dependencies and Integration Points
Depends on WiredTiger cursor configuration parsing and transaction error handling.

## Risks and Edge Cases
The edge is differentiating API validation failure from an operation failure that should force transaction rollback.

## Test Signals
Both commits must succeed after the expected `next_random.*boolean` errors.
