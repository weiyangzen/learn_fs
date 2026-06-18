# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor03.py

## Purpose
Exercises atomic schema create/drop logging paths for files, simple tables, column groups, and indexes.

## APIs, Types, And Functions
Defines `test_metadata03` with logging enabled and scenarios for file, table with column group, table with index, and simple table. Helpers count whole log records through a `log:` cursor and provide `verify_logrecs`.

## Control Flow, State, And Persistence
The test counts existing log records, creates the main URI with optional column definitions, optionally creates a column group or index, then drops the main URI. Intended behavior is that schema operations log as atomic records rather than many individual records. The current `verify_logrecs` assertion is commented out pending WT-3965, so the test walks the log and performs the operations but does not enforce the expected count.

## Dependencies, Integration, Risks, And Test Signals
Depends on the log cursor, schema metadata logging, and table/index/column-group creation. The major risk is reduced regression strength because the count assertion is disabled. Existing signals are operation success and log cursor traversal, not strict atomicity validation.
