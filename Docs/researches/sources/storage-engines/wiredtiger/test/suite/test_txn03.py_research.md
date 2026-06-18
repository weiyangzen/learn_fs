# sources/storage-engines/wiredtiger/test/suite/test_txn03.py

## Purpose
`test_txn03.py` verifies transaction cursor behavior for update/rollback/commit on row-store, variable-length column-store, and fixed-length column-store style scenarios.

## Important APIs, Types, and Functions
The class defines `test_ops` over scenarios carrying create parameters, key, and two values. It uses `session.create`, cursor assignment/search, `begin_transaction`, `rollback_transaction`, and `commit_transaction`.

## Control Flow
The test creates a table, inserts an initial value in a transaction, checks visibility before and after rollback, writes a second value in a transaction, checks same-transaction visibility, commits, and checks that the committed value remains visible.

## State and Persistence Behavior
All state is table-local and transactional. The test confirms that rolled-back writes do not persist and committed writes do, across key formats.

## Dependencies and Integration Points
Depends on `wtscenario.make_scenarios`, the WiredTiger cursor mapping interface, and transaction APIs.

## Risks and Edge Cases
Column-store record numbers and row-store string keys exercise different cursor key paths. A rollback bug could leave dirty cursor state visible.

## Test Signals
Searches and value reads before rollback, after rollback, before commit, and after commit match the scenario values.
