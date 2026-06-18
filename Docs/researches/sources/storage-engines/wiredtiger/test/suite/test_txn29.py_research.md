# sources/storage-engines/wiredtiger/test/suite/test_txn29.py

## Purpose
`test_txn29.py` verifies that a transaction which fails commit after logging an invalid timestamp does not leave rolled-back data recoverable after crash restart.

## Important APIs, Types, and Functions
The class defines `test_transaction_logging`, uses `wiredtiger.diagnostic_build` skip logic, logged and non-logged files, timestamped `commit_transaction(sync=on,commit_timestamp=...)`, `assertRaisesException`, `simulate_crash_restart`, and `WT_NOTFOUND`.

## Control Flow
The test writes `aaaa` to both logged and non-logged files at timestamp 20, then attempts to write `bbbb` at timestamp 10 and expects commit failure. After crash restart, it verifies the non-logged file has no key and the logged file still has `aaaa`, not `bbbb`.

## State and Persistence Behavior
Logged table data should recover the first transaction only. The non-logged table's failed update must not be durable.

## Dependencies and Integration Points
Depends on timestamp validation, transaction logging, crash restart helper, and diagnostic-build behavior.

## Risks and Edge Cases
It specifically protects against a logged transaction becoming unrecoverably partially durable after commit failure.

## Test Signals
The second commit raises, recovery shows `uri2` not found and `uri1` value `aaaa`, and expected timestamp-usage stderr is ignored if present.
