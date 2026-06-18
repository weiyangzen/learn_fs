<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate15.py

Purpose: Ensures read-only database reads of fast-truncated pages do not leave cache stuck or produce rollback under tight cache settings.

Important APIs/types/functions: `test_truncate15` uses `session.truncate`, prepared transaction commit/durable timestamps, `stat.conn.rec_page_delete_fast`, read-only reopen config, `check`, and `evict_cursor` helper. It skips disaggregated storage because readonly connections are not supported.

Control flow: The test writes 100,000 rows at timestamp 10, stabilizes them, reopens, fast-truncates half the table in a prepared transaction with commit 25 and durable 30, verifies fast-delete occurred, advances stable to 30 and checkpoints, then reopens readonly with a 1MB cache. It reads at timestamps 10, 20, 25, and 30 and treats `WT_ROLLBACK` during reads as failure.

State and persistence behavior: The database is reopened readonly after checkpointing fast-delete metadata. The test verifies read-only cache behavior while reading deleted pages at multiple timestamps.

Dependencies and integration points: Integrates readonly connection mode, fast-delete, prepared durable timestamps, cache eviction settings, and timestamp reads.

Risks: The test is large by design; 50,000 rows was insufficient to trigger the original issue. Cache pressure makes false retries undesirable, so rollback is explicitly trapped and failed.

Test signals: Positive fast-delete count and successful read checks without `WT_ROLLBACK`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate15.py -->
