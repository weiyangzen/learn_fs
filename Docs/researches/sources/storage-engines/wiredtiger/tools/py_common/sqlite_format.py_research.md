# sources/storage-engines/wiredtiger/tools/py_common/sqlite_format.py

Purpose: detects and reads SQLite page-log databases containing disaggregated page records, reconstructing page chains for the shared disaggregated decoder.

Important APIs and control flow: `is_sqlite3_file()` checks the SQLite signature unless stdin is used. `_load_rows_for_page()` finds non-discarded base pages for a page id, warns when multiple bases exist, picks the newest base LSN, and returns rows at or after that base in descending LSN order. `_load_row_for_lsn()` selects one non-discarded row. `_rows_to_disagg_pages()` converts SQLite rows into `disagg.DisaggPage` objects using `WT_PAGE_LOG_DELTA`. `_load_disagg_pages_all()`, `_load_disagg_pages_for_lsn()`, and `_load_disagg_pages_for_page_id()` implement the selection modes. `load_disagg_pages()` gives LSN precedence over page-id chain traversal. `process_sqlite_file()` feeds loaded chains to `disagg.process_disagg_pages()`.

State and persistence behavior: opens SQLite read connections and returns in-memory page chains. It does not modify the SQLite database. Page limits apply to loaded row count during all-pages mode.

Dependencies and integration points: selected automatically by `wt_binary_decode` when the input file signature matches SQLite. Depends on `sqlite3`, `DecodeOptions`, and `py_common.disagg`.

Risks: the schema is assumed to contain `pages(table_id,page_id,lsn,backlink_lsn,base_lsn,flags,discarded,page_data)`. Multiple base page handling chooses the newest and only logs a warning. Rows are ordered by `lsn DESC`, not by explicitly following `backlink_lsn`, so malformed chains may still be decoded in timestamp order. All-pages mode iterates distinct page ids without deterministic ordering.

Test signals: `test_sqlite_format.py` covers signature detection, latest-base selection, LSN precedence, page limit behavior, discarded-row filtering, base-chain ordering, and page-id/LSN mismatch errors.
