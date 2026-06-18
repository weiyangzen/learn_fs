# sources/storage-engines/wiredtiger/test/suite/test_txn30.py

## Purpose
`test_txn30.py` checks that a failed schema operation inside a transaction does not block committing data changes made in that transaction.

## Important APIs, Types, and Functions
The class defines `test_txn30`, uses `session.create(..., exclusive=true)`, `begin_transaction`, cursor update, `assertRaises`, and `commit_transaction`.

## Control Flow
It creates a file exclusively, begins a transaction, inserts key 1, attempts to create the same object again with exclusive create and expects failure, then commits the transaction.

## State and Persistence Behavior
The data update should commit despite the schema create failure. The test does not reopen or read the value; success is no transaction error flag from the failed schema operation.

## Dependencies and Integration Points
Depends on WiredTiger schema API error handling and transaction error-state rules.

## Risks and Edge Cases
Like `test_txn12`, this guards the boundary between API/schema validation errors and transaction-fatal errors.

## Test Signals
The duplicate create raises `WiredTigerError`, and the following commit succeeds.
