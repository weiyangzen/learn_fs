# sources/storage-engines/wiredtiger/tools/test/test_sqlite_format.py

Purpose: unit tests for SQLite disaggregated page-log loading and selection semantics.

Important APIs and control flow: `_create_test_db()` creates a temporary SQLite database with a `pages` table and sample rows covering base pages, deltas, multiple bases, and discarded records. Tests cover `is_sqlite3_file()`, newest-base selection with warning, LSN-specific selection, single-base selection, all-pages page limit, LSN without page id, discarded-row filtering, page-id chain ordering, and page-id/LSN mismatch errors. `tearDown()` removes the temp database.

State and persistence behavior: creates and deletes a temporary `.db` file for each test case. No repository files are modified.

Dependencies and integration points: directly covers `py_common.sqlite_format` and indirectly verifies conversion to `disagg.DisaggPage` metadata.

Risks: the synthetic `page_data` is arbitrary bytes, so these tests validate row selection and metadata conversion rather than downstream page parsing. Multiple-base behavior is intentionally warning-and-select-newest; future stricter semantics would require test changes.

Test signals: pass provides strong coverage for SQLite query filters, discarded handling, page/LSN precedence, and delta flag conversion.
