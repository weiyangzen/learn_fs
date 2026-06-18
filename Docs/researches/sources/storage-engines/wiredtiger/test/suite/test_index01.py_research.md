# sources/storage-engines/wiredtiger/test/suite/test_index01.py

Purpose: basic coverage for WiredTiger secondary indexes over a table with composite keys, named columns, and multiple index key definitions.

Important APIs and functions: `test_index01` creates `table:test_index01` with `key_format=Si`, `value_format=SSii`, and columns `(name,ID,dept,job,salary,year)`. It creates six indexes over different column combinations. Helpers wrap table/index cursor creation, insert/update/remove operations, duplicate insertion checks, and existence checks.

Control flow: tests cover empty table lookup and empty indexes, insert and expected index cursor order/content, update including nonexistent updates, insert with overwrite including duplicate rejection, delete and index cleanup, and exclusive index creation failure after non-exclusive recreation.

State and persistence behavior: index state is automatically maintained when base records are inserted, overwritten, updated, or removed. No checkpoint is required; this is logical cursor/index consistency.

Dependencies and integration points: uses the core WiredTiger cursor API, index cursor projection behavior, `WT_NOTFOUND`, duplicate-key error handling, and `dropUntilSuccess`.

Risks and edge cases: expected index rows are hard-coded as rendered Python lists, so output order/projection changes are visible. Coverage is functional but limited to a small number of records.

Test signals: exact index iteration output matches expected strings; duplicate insert raises; nonexistent update returns `WT_NOTFOUND`; delete leaves all indexes empty; exclusive recreate raises.
