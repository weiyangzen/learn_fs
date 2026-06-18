# sources/storage-engines/wiredtiger/test/suite/test_index03.py

Purpose: regression coverage for creating an index after a table already contains enough data to require bulk index population.

Important APIs and functions: `test_index03` uses helper methods `key` and `value` to generate string keys and values, creates a table, inserts records, then creates an index over a value column.

Control flow: the test creates a table with named columns, inserts a range of generated rows, creates the index after data exists, and then validates index behavior through cursor operations.

State and persistence behavior: the important state transition is index creation on a populated table. WiredTiger must scan existing records and build a consistent index rather than only indexing future writes.

Dependencies and integration points: depends on table/index DDL, column metadata, cursor insertion, and index backfill.

Risks and edge cases: the file is small and targets a specific populated-create path. It does not cover updates/removals after index creation because `test_index01` covers those basics.

Test signals: successful index creation and expected index lookup/iteration behavior over pre-existing records.
