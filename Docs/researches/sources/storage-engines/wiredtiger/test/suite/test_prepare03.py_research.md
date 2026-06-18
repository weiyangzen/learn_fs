# sources/storage-engines/wiredtiger/test/suite/test_prepare03.py

## Purpose
Checks that cursor APIs are rejected in prepared transaction state and still work normally outside that state.

## APIs, Types, And Functions
Defines `test_prepare03` with file/table and row/column scenarios. Helpers generate row or record-number keys, generate values, and assert unpositioned cursor key/value errors. Tested cursor APIs include `insert`, `next`, `get_key`, `get_value`, `prev`, `search`, `update`, `remove`, `reserve`, `reconfigure`, and `search_near`.

## Control Flow, State, And Persistence
The test creates a table, opens a cursor, then for inserts and cursor traversal repeatedly begins a transaction, prepares it, asserts the selected cursor operation fails with prepared-state error, resolves the transaction, and performs the corresponding operation outside prepared state. It verifies forward and backward iteration order and exercises update/remove after a prepared-state rejection.

## Dependencies, Integration, Risks, And Test Signals
Depends on cursor-state enforcement during prepared transactions and normal cursor behavior afterward. It skips a URI equality assertion under the disagg hook because URIs may be rewritten to layered. Risks are allowing cursor reads/writes in prepared state or leaving the cursor corrupted after rejected calls. Signals are expected exceptions plus successful normal operations.
