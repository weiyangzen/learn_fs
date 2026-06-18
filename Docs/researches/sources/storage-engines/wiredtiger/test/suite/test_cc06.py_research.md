# sources/storage-engines/wiredtiger/test/suite/test_cc06.py

Purpose: verifies checkpoint cleanup ignores empty or newly created files.

Important APIs/types/functions: inherits `test_cc_base`, uses `SimpleDataSet`, `make_scenarios`, dsrc stat `checkpoint_cleanup_pages_visited`, `wait_for_cc_to_run`, and `reopen_conn`.

Control flow: create an empty dataset for `table:cc06` with logging disabled and the scenario key/value format, set oldest/stable to 10, force checkpoint cleanup, assert the table-level pages-visited stat is zero, reopen the database, force cleanup again, and assert the same stat remains zero.

State/persistence behavior: tests the empty-file metadata state before and after reopen. Cleanup should not scan pages that do not exist or newly created btrees with no obsolete content.

Dependencies/integration: dsrc statistics, checkpoint cleanup, empty btree handling, connection reopen, column/integer row scenarios.

Risks/test signals: failure is nonzero page visits, indicating wasted or incorrect cleanup work on empty files.
