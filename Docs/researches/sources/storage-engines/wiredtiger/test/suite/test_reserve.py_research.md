# sources/storage-engines/wiredtiger/test/suite/test_reserve.py

Purpose: validates `WT_CURSOR.reserve` semantics on supported row/column/file/table datasets and rejection on invalid cursor states or non-standard cursor types.

Important APIs and types: `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `make_scenarios`, cursor `reserve`, `update`, `insert`, `remove`, transaction commit/rollback, and special cursors such as backup/config/log/metadata/statistics.

Control flow: the main test populates data, updates a record, asserts reserve fails for a missing record, reserves existing records with commit and rollback, reserves then updates, and verifies another transaction cannot update a reserved record. Additional tests check reserve requires a key, requires a running transaction, returns the current value on success, and is unsupported on bulk/dump and system cursors.

State and persistence behavior: reserve creates transactional write intent without changing value unless followed by update. Commit and rollback paths are exercised, along with conflict behavior from another session.

Dependencies and integration points: cursor API contracts, transaction conflict detection, dataset abstractions, index/complex table cursor wrappers, and hook-specific disagg behavior for bulk cursor support.

Risks: there is a likely copy/paste comment mismatch where the "reserve then update and rollback" loop actually commits; research consumers should inspect before changing semantics.

Test signals: reserve returns 0 and current value when valid, raises required-key/no-transaction/unsupported errors in invalid modes, and conflicting update from another session raises `WiredTigerError`.
