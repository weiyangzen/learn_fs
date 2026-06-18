<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat05.py

Purpose: verifies that size-only data-source statistics cursors can be opened and walked across table/file types, in-memory configurations, and complex datasets while a table grows.

Important APIs/types/functions: `test_stat_cursor_config` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `conn_config=statistics=(fast)`, helper `openAndWalkStatCursor`, and dataset cursor helpers. Scenarios cover file/table row, file/table var, in-memory row/var, and complex-row table.

Control flow: choose row or variable-length column key/value formats, populate 100 records, open and fully iterate a `statistics=(size)` cursor, then insert records 100 through 40000 while reopening/walking the size stats cursor every 100 records, and once again at the end.

State and persistence behavior: size stats must remain available during ongoing growth and under fast database statistics. In-memory scenarios have no disk size in the same sense, but cursor open/walk must still be valid.

Dependencies/integration points: covers size stats, fast stats compatibility, large insert loops, file/table/in-memory data sources, and complex dataset backing objects. Risks are runtime and scenario-specific size stat availability; signal is absence of cursor open/iteration failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat05.py -->
