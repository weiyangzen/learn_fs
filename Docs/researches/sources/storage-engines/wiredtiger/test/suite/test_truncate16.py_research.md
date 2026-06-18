<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate16.py

Purpose: Verifies reads from a page fast-truncated by an unresolved prepared transaction return prepare conflict and instantiate only the needed deleted page.

Important APIs/types/functions: Uses `session.truncate`, `prepare_transaction`, read timestamp transactions, `stat.conn.rec_page_delete_fast`, `stat.conn.cache_read_deleted`, expected `WiredTigerError` with prepare conflict text, and optional checkpoint scenarios.

Control flow: The test writes/stabilizes 10,000 rows at timestamp 10, reopens, starts a second-session transaction that fast-truncates the middle half and prepares at timestamp 20, optionally checkpoints, then reads a key in the truncated range at timestamp 30. The read must raise prepare conflict. It then rolls back the prepared transaction and scans the full table.

State and persistence behavior: Prepared fast-delete metadata remains unresolved. Reading one key should instantiate one deleted page for conflict handling. Rolling back the prepared transaction should not instantiate additional pages.

Dependencies and integration points: Integrates prepared transaction visibility, fast-delete page instantiation, checkpoint interaction, statistics, and row/column formats.

Risks: A regression could either miss the prepare conflict, instantiate too many pages, or leave rollback unable to restore the table view.

Test signals: Expected prepare conflict, `cache_read_deleted` equals 1 for fast-delete cases, full-table scan after rollback, and unchanged deleted-page read count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate16.py -->
