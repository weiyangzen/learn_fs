# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor02.py

## Purpose
Tests metadata cursor behavior when table metadata is incomplete because a column group or backing file has been dropped independently.

## APIs, Types, And Functions
Defines `test_metadata_cursor02`, skipped for disaggregated and tiered hooks. It uses scenarios for `metadata:` versus `metadata:create` and invalidation by `colgroup` versus `file` drops. Helpers reopen, force-drop existing tables, and recreate three tables.

## Control Flow, State, And Persistence
For each table, the test recreates all three, then drops either the table's column group or file URI to make one table incomplete. It opens the metadata cursor, counts entries starting with `table:`, and for create cursors checks captured error output for missing metadata information. Plain metadata still lists all table entries; create metadata omits the invalid one.

## Dependencies, Integration, Risks, And Test Signals
Depends on attached storage internals, metadata cleanup messages, and `metadata:create` expansion. Risks are crashing on incomplete metadata or returning invalid expanded entries. Signals are count differences between cursor modes and expected diagnostic patterns.
