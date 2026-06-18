# sources/storage-engines/wiredtiger/test/suite/test_txn27.py

## Purpose
`test_txn27.py` validates the error-info API for rollback errors, ensuring the saved rollback reason distinguishes write conflicts from oldest-for-eviction rollback.

## Important APIs, Types, and Functions
The class inherits `error_info_util`, defines `test_rollback_reason`, and uses `assert_error_equal`, `WT_ROLLBACK`, `WT_WRITE_CONFLICT`, `WT_OLDEST_FOR_EVICTION`, `WT_NONE`, small cache configuration, and `SimpleDataSet`.

## Control Flow
Session1 updates key 5 inside a transaction. Session2 tries to update the same key and receives a write conflict; the saved error reason is checked. After rollback clears the error, session1 starts a huge update that pins cache state, sleeps for accounting, then another update triggers rollback due to oldest pinned transaction ID.

## State and Persistence Behavior
No successful durable state is central; it stresses active transaction conflict and eviction rollback metadata.

## Dependencies and Integration Points
Depends on `error_info_util`, WiredTiger rollback reason tracking, cache pressure, and time-based accounting delay.

## Risks and Edge Cases
The eviction rollback path may be timing-sensitive due to `time.sleep(2)`. Error text and reason constants must remain stable.

## Test Signals
Saved error info matches write conflict, clears after rollback, then matches oldest-for-eviction for the cache-pressure rollback.
