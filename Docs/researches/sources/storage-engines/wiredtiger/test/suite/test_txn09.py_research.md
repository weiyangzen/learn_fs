# sources/storage-engines/wiredtiger/test/suite/test_txn09.py

## Purpose
`test_txn09.py` is another transaction operation matrix focused on visibility across up to four operations and commit/rollback combinations without the heavier log-file inspection of neighboring tests.

## Important APIs, Types, and Functions
The class defines scenario dimensions for table types and operation/transaction pairs, plus `conn_config`, `check`, `check_all`, and `test_ops`.

## Control Flow
Each scenario creates a table, performs sequential transactional operations, updates current and committed dictionaries, checks current-session visibility, snapshot/read-committed/read-uncommitted visibility from another session, and resolves each transaction.

## State and Persistence Behavior
State is mostly in the table and active transaction manager. The key invariant is that uncommitted current changes are only visible where allowed and committed state evolves only after commit.

## Dependencies and Integration Points
Depends on `wtscenario.make_scenarios`, `suite_subprocess`, and WiredTiger transaction/isolation APIs.

## Risks and Edge Cases
Scenario pruning means the selected subset must remain representative. Multi-operation sequencing can reveal stale expected-state handling or isolation regressions.

## Test Signals
`check_all` dictionary comparisons across isolation levels must match `current` and `committed`.
