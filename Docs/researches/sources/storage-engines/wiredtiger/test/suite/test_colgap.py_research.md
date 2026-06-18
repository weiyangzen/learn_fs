# sources/storage-engines/wiredtiger/test/suite/test_colgap.py

Purpose: covers variable-length column-store gaps and very large record numbers near the unsigned 64-bit maximum. It ensures traversal, search, update, and removal remain efficient and correct.

Important APIs and types: `SimpleDataSet`, `simple_key`, `simple_value`, cursor `next`/`prev`/`search`/`remove`, `wiredtiger.WT_NOTFOUND`, and `make_scenarios`.

Control flow: `test_column_store_gap` inserts sparse recnos with huge gaps, scans forward/backward before and after reopen. `test_column_store_gap_traverse` adds middle in-memory records after reopening and verifies merged traversal order. `test_colmax` creates file/table column stores, optionally bulk-loads, inserts a record at a huge or maximum recno, reopens optionally, then searches, updates, and removes it.

State and persistence behavior: tests both in-memory update lists and persisted disk pages, including traversal that merges on-disk records with new in-memory records. Large recnos test maximum key encoding and column-store namespace gaps.

Dependencies and integration points: variable-length column-store implementation, bulk cursor mode, file/table URI handling, and scenario matrix across value formats and reopen modes.

Risks: performance is implicit; a regression may hang rather than fail quickly. The `nentries` class field is mutated per test.

Test signals: exact forward/backward key sequences, successful lookup/update of huge recno, and `WT_NOTFOUND` after removal.
