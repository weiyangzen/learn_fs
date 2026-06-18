<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor20.py

Purpose: tests duplicate-key error behavior and value state after inserting with `overwrite=false`.

Important APIs and control flow: scenarios cover row-string and variable-column keys, with in-memory and reopen/on-disk variants. The test populates a 100-row `SimpleDataSet`, optionally reopens, opens a cursor with `overwrite=false`, sets an existing key with a different value, asserts insert raises `WT_DUPLICATE_KEY`, and then asserts `get_value()` returns the existing stored value.

State, persistence, and dependencies: state is a populated table either in cache or read after reopen. Dependencies are `SimpleDataSet`, `suite_subprocess`, `wiredtiger`, cursor overwrite config, and duplicate-key error matching.

Integration points: covers insert duplicate handling and cursor value replacement semantics after failed insert across memory/disk.

Risks and test signals: semantics are subtle: after duplicate failure, cursor value should reflect the existing record, not the attempted value. Pass signal is duplicate error plus exact existing value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor20.py -->
