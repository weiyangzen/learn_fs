# sources/storage-engines/wiredtiger/test/suite/test_pack.py

## Purpose
Tests public packing/unpacking behavior for multiple value formats through table storage and index lookup.

## APIs, Types, And Functions
Defines `test_pack` with helper `check(fmt, *v)`. It creates a table with value format `fmt`, creates an inverse index on all value columns, inserts one key/value tuple, reads the table value, and searches the index by value.

## Control Flow, State, And Persistence
`test_packing` calls `check` for integer groups, fixed and variable strings, strings containing nul padding, byte-array formats, empty byte arrays, and signed string formats. Each generated table and index persists one record, then the test validates both direct table unpacking and index key packing.

## Dependencies, Integration, Risks, And Test Signals
Depends on WiredTiger format strings, column definitions, index packing, and Python API return conventions for single versus multiple values. Risks are mismatched fixed-size packing, null/empty byte handling, or secondary index encoding divergence. Signals are equality of unpacked values and successful inverse index lookup returning key 1234.
