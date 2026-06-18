<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat13.py

Purpose: checks that `btree_maximum_depth` is computed and remains discoverable after reopen for small two-level row and column-store trees.

Important APIs/types/functions: `test_stat13` uses `SimpleDataSet`, `make_scenarios`, `stat.dsrc.btree_maximum_depth`, `session.checkpoint`, `reopen_conn`, and dataset cursor helpers.

Control flow: populate 100 records in a row or column table, checkpoint, assert maximum depth is 2, reopen the connection, read one key to instantiate the btree depth information, and assert depth is still 2.

State and persistence behavior: the checkpoint persists the btree. After reopen, the maximum-depth statistic is populated only after an operation touches the table, so the test performs a cursor search before reading stats.

Dependencies/integration points: covers btree depth accounting, checkpoint/reopen behavior, row and column key formats, and data-source stats. Risks include page-size changes that alter tree depth; signals are exact depth value before and after reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat13.py -->
