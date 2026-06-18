# sources/storage-engines/wiredtiger/test/suite/test_txn20.py

## Purpose
`test_txn20.py` gives a focused isolation-level check for dirty reads and non-repeatable reads across string row and column-store key formats.

## Important APIs, Types, and Functions
The class defines scenarios for `read-uncommitted`, `read-committed`, and `snapshot`, plus `test_isolation_level`. It uses one writer session and one reader session with `begin_transaction('isolation=...')`.

## Control Flow
The test writes an old value, begins a writer transaction, updates the key without committing, then starts a reader transaction at the selected isolation. Read-uncommitted should see the new value while the other levels see old. After writer commit, snapshot still sees old; read-committed and read-uncommitted see new.

## State and Persistence Behavior
State is active in-memory transactional visibility; the table contains one key whose visible version changes by isolation and commit timing.

## Dependencies and Integration Points
Depends on WiredTiger isolation implementation and scenario key conversion.

## Risks and Edge Cases
The test distinguishes dirty reads from non-repeatable reads. Column-store record-number keys must behave the same as row-store keys.

## Test Signals
Value assertions before and after writer commit match the selected isolation semantics.
