<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate10.py

Purpose: Verifies fast-truncate prepared at 20, committed at 25, and durable at 30 behaves correctly across stable timestamp/checkpoint combinations.

Important APIs/types/functions: `test_truncate10` uses `session.truncate`, prepared transaction APIs, `stat.conn.rec_page_delete_fast`, `check` with read timestamps, snapshot isolation, and scenario dimensions for stable timestamp and checkpoint.

Control flow: The test writes 10,000 rows at timestamp 10, marks stable, reopens, truncates half the table, prepares at 20, commits at 25 with durable 30, checks fast-delete stats, optionally advances stable to 10/20/25/30 and checkpoints, then reads at 10, 20, 25, and 30 to verify expected row counts.

State and persistence behavior: It stresses commit timestamp versus durable timestamp for fast-delete visibility. Reads before commit see all rows; reads at commit/durable see half the rows deleted.

Dependencies and integration points: Integrates prepared transaction timestamp ordering, durable timestamp handling, fast-delete stats, checkpoint, stable timestamp, and tiered hook variability.

Risks: The comment notes reading between commit and durable can be problematic but is currently permitted. Any semantic change there would affect the test.

Test signals: Fast-delete page count, plus exact row counts at each read timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate10.py -->
