# sources/storage-engines/wiredtiger/test/suite/test_overwrite.py

## Purpose
Tests cursor `overwrite=false` semantics for insert, remove, and update across files, simple tables, complex tables, indexes, and key formats.

## APIs, Types, And Functions
Defines `test_overwrite` with scenarios over dataset type, key format, and several syntactically different cursor configs that all disable overwrite. It uses `SimpleDataSet`, `ComplexDataSet`, `SimpleIndexDataSet`, duplicate cursors, and `wiredtiger.WT_NOTFOUND`.

## Control Flow, State, And Persistence
Each method populates 100 rows and opens cursors with and without overwrite. Insert tests fail on existing keys with overwrite off, allow duplicate cursor override when supported, and allow inserts on new keys. Remove tests show overwrite no longer changes missing-key behavior: missing removes fail in both modes. Update tests fail on missing keys with overwrite off but upsert with overwrite on.

## Dependencies, Integration, Risks, And Test Signals
Depends on dataset helpers and cursor config parsing, including fast-path and normal parser cases. Risks are regressions in overwrite config parsing, remove semantics, or layered duplicate cursor support. Signals are exceptions, zero returns, and `WT_NOTFOUND` for each operation class.
