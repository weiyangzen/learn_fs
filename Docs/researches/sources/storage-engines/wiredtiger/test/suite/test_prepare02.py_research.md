# sources/storage-engines/wiredtiger/test/suite/test_prepare02.py

## Purpose
Ensures forbidden `WT_SESSION` APIs return the expected errors while a transaction is prepared, and permitted operations still work.

## APIs, Types, And Functions
Defines `test_prepare02`, skipped for tiered storage and mixed with `suite_subprocess`. It uses session APIs including `reconfigure`, `open_cursor`, `alter`, `create`, `compact`, `drop`, `log_flush`, `reset`, `salvage`, `truncate`, `verify`, `begin_transaction`, `prepare_transaction`, `checkpoint`, `breakpoint`, commit, rollback, and close.

## Control Flow, State, And Persistence
The test creates a table, writes one key in a transaction, prepares it, then calls many session methods and asserts `not permitted in a prepared transaction` or `not permitted in a running transaction` where applicable. It verifies these errors do not poison the transaction by committing successfully. It then separately checks commit after prepare, timestamp-setting after prepare, rollback after prepare, and close after prepare.

## Dependencies, Integration, Risks, And Test Signals
Depends on prepared transaction state-machine enforcement and Python API exception messages. Risks are allowing schema/maintenance operations while prepared or setting transaction error flags for rejected operations. Signals are exact error regexes and successful permitted resolution paths.
