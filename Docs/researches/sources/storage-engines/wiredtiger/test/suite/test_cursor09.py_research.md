<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor09.py

Purpose: regression test for WT-2217: `WT_CURSOR.insert` should not leave the cursor positioned with key/value set.

Important APIs and control flow: scenarios cover file/table, row/column, and complex datasets. The test populates 100 records, opens a cursor, assigns `cursor[ds.key(10)] = ds.value(10)` to perform an insert/update operation, then immediately calls `cursor.search()` without resetting a key and expects a `requires key be set` error.

State, persistence, and dependencies: state is a populated dataset and cursor key/value flags after insert. Dependencies include `SimpleDataSet`, `ComplexDataSet`, `wiredtiger`, and error-message assertions.

Integration points: targets cursor internal state cleanup after insert across access methods and complex table layouts.

Risks and test signals: this is narrow but important for API consistency. A pass means insert clears the required key state; a failure indicates stale key positioning or incorrect API state tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor09.py -->
