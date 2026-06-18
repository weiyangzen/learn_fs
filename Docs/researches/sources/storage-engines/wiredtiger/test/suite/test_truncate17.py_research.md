<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate17.py

Purpose: Checks data-source statistics for a prepared fast-truncate and confirms stats instantiate deleted pages without changing page counts before rollback.

Important APIs/types/functions: Adds `stat_tree` over `statistics:<uri>` to read btree entry and page counts. Uses `session.truncate`, `prepare_transaction`, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, and optional checkpoint scenarios.

Control flow: The test writes 10,000 rows at timestamp 10, stabilizes and reopens, records baseline btree entry/page counts, reopens again, prepares a second-session fast-truncate of the middle half, optionally checkpoints, then reads data-source stats. Stats should show half the entries but unchanged page counts. It verifies `cache_read_deleted` equals the number of fast-deleted pages, then rolls back and checks that value remains unchanged.

State and persistence behavior: Data-source stats are non-transactional/read-uncommitted, so they observe the prepared truncate's logical entry count while the physical deleted pages still exist.

Dependencies and integration points: Integrates btree statistics, prepared fast-delete metadata, checkpoint, page instantiation counters, and row/column page-stat distinctions.

Risks: Stats can accidentally instantiate or discard pages, or report transactionally hidden values. This test deliberately codifies the read-uncommitted behavior.

Test signals: Baseline entries equal nrows, post-prepare entries equal nrows/2, page tuple equals baseline, and `cache_read_deleted == fastdelete_pages`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate17.py -->
