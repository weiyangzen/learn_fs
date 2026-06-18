# sources/storage-engines/wiredtiger/test/cppsuite/src/main/crud.h

Purpose: Provides inline CRUD helpers that translate WiredTiger cursor return codes into transaction state for workload operations.

Important APIs/types/functions: `crud::insert`, `crud::update`, and `crud::remove` set cursor key/value as needed, invoke the WT cursor method, mark the `transaction` for rollback on `WT_ROLLBACK`, return false for retry/abort handling, and die on unhandled errors.

Control flow: helpers are intended to be called inside a transaction object that can later roll back if any operation sees `WT_ROLLBACK`.

State and persistence: successful calls mutate persistent table data through the cursor. On rollback conflicts they only mark in-memory transaction state.

Dependencies/integration: depends on `scoped_cursor`, `transaction`, `wiredtiger.h`, and `test_util`.

Risks and test signals: `WT_NOTFOUND` on remove/update is treated as an unhandled fatal error, so callers must choose existing keys or handle search separately. Rollback handling is explicit and observable via transaction state.
