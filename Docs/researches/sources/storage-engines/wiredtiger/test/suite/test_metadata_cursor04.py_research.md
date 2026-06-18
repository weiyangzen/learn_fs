# sources/storage-engines/wiredtiger/test/suite/test_metadata_cursor04.py

## Purpose
Checks that `metadata:create` exposes expected logging configuration for simple and complex tables.

## APIs, Types, And Functions
Defines `test_metadata04` with logged connection config. Helper `check_meta` opens `metadata:create`, searches a URI, prints metadata, and optionally asserts `log=(enabled=false)` is present.

## Control Flow, State, And Persistence
The complex-table test creates a table with `log=(enabled=false)`, column definitions, a column group, and an index, then checks the column group and index expanded metadata include logging disabled while the top-level table is printed but not checked. The simple-table test creates one non-logged table and asserts its create metadata includes `log=(enabled=false)`.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata create cursor expansion and schema configuration propagation to indexes and column groups. Risks include losing per-object log settings in generated metadata. Signals are direct metadata substring assertions.
