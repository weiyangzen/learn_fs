<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat03.py

Purpose: verifies that resetting a data-source statistics cursor refreshes values, and that complex datasets report multiplied entry counts through table, index, and column-group stats.

Important APIs/types/functions: `test_stat_cursor_reset` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `stat.dsrc.btree_entries`, helper `stat_cursor`, and dataset methods `colgroup_count`, `index_count`, `index_name`, and `colgroup_name`.

Control flow: populate 100 entries for file/table simple row/var and complex table scenarios. Open a stats cursor and assert initial `btree_entries`, insert one more record through a data cursor, check the stale stats cursor still reports the old count, call `statc.reset`, and verify the updated count. For complex datasets, also check a direct index and colgroup stats cursor reports the base row count.

State and persistence behavior: the stats cursor snapshots values until reset. Complex table stats aggregate multiple backing btrees, so count state differs between the logical table and individual btrees.

Dependencies/integration points: covers statistics cursor reset semantics, dataset abstraction, index/colgroup backing stores, and key/value formats. Risks include assumptions about entry multiplication; signals are exact counts before and after reset.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat03.py -->
