# sources/storage-engines/wiredtiger/test/suite/test_checkpoint32.py

Purpose: tests cursor tree-walk optimization that skips in-memory reconciled deleted pages after checkpoint.

Important APIs and types: `SimpleDataSet`, `stat.conn.cursor_tree_walk_inmem_del_page_skip`, transaction-per-key inserts/removes, and checkpoint.

Control flow: populate a table, insert 1,000 rows, hold a read transaction open, remove all data in individual transactions, checkpoint, read the statistic baseline, scan the table expecting no rows, read the statistic again, and assert it increased.

State and persistence behavior: deleted pages remain represented in memory while an old reader is open. After checkpoint, cursor traversal should skip the in-memory deleted pages rather than walking them normally.

Dependencies and integration points: relies on cursor traversal statistics and the presence of an active reader to keep deleted page state relevant. Covers row-store and column-store formats plus precise/fuzzy checkpoint.

Risks: precise checkpoint requires stable timestamp initialization. Statistic changes may vary if cursor traversal implementation changes.

Test signals: table scan returns zero rows and `cursor_tree_walk_inmem_del_page_skip` increases.
