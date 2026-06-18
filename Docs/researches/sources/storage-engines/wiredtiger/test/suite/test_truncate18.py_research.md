<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate18.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate18.py

Purpose: Regression test for verification when deleted pages full of obsolete values are optimized into physically empty pages, especially near the leftmost leaf.

Important APIs/types/functions: Uses `session.truncate`, `verifyUntilSuccess`, small `internal_page_max`, timestamp advancement, checkpoints, repeated `reopen_conn`, and `stat.conn.rec_page_delete_fast`.

Control flow: The test writes baseline data at timestamp 10, stabilizes and reopens, truncates either the front or back 7/8 of the table at timestamp 20, verifies fast-delete occurred, stabilizes and reopens, advances oldest so baseline data is obsolete, writes and deletes key 1 to force reconciliation of the first leaf/internal pages, stabilizes/ages out that scratch change, checkpoints, reopens, and runs verify.

State and persistence behavior: The scenario creates globally visible fast-deleted pages containing obsolete values, then forces partial internal-page reconciliation. The key concern is whether verify can handle empty-page optimization without losing physical key-order information.

Dependencies and integration points: Integrates reconciliation, verification, obsolete-value cleanup, fast-delete, oldest/stable advancement, and row/column formats.

Risks: Comments note a known assertion scenario in verify. The test is specific and relies on tree shape from small internal pages and 10,000 rows.

Test signals: Positive fast-delete stats and successful `verifyUntilSuccess(uri=ds.uri)` after the constructed state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate18.py -->
