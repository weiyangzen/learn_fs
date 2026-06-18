# sources/storage-engines/wiredtiger/test/suite/test_bug017.py

Purpose: regression for WT-2987, where opening a cursor on an incomplete table with declared but missing column groups could crash.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `session.create`, `session.open_cursor`, and `assertRaisesWithMessage`.

Control flow: create `table:bug17` with key/value formats and `columns=(id,country,year,population),colgroups=(main,population)` but without creating the column group objects. Then attempt `open_cursor("table:bug17(country)")` and expect an error matching `/column groups/`.

State/persistence behavior: creates incomplete metadata intentionally. The invariant is that cursor open validates column group completeness and reports an error instead of dereferencing missing structures.

Dependencies/integration: touches table metadata, projection cursor parsing, and column group validation.

Risks/test signals: narrow message-fragment assertion. The absence of a crash is the core signal.
