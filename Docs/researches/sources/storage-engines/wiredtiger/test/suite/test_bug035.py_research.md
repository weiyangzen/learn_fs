# sources/storage-engines/wiredtiger/test/suite/test_bug035.py

Purpose: regression for WT-13716 involving selective backup and fast truncate. It verifies that history-store pages for excluded tables do not reappear after opening the backup and shutdown.

Important APIs/types/functions: `backup_base`, `take_selective_backup`, `wiredtiger_open`, `stat.conn.rec_page_delete_fast`, `backup_restore_target`, `verify_metadata=true`, and helper `add_timestamp_data`.

Control flow: create 10 tables, write 9 timestamped generations of 1,000 records to each, set stable timestamp 15, checkpoint, create a backup directory, take a selective backup excluding the last five tables, open the backup with `backup_restore_target` naming the first five tables, assert fast truncate statistic is greater than zero, close, reopen with `verify_metadata=true`, and close.

State/persistence behavior: opening the selective backup runs rollback-to-stable and truncates history-store pages for tables not in the restore target. Metadata and HS must not retain excluded tables after shutdown/reopen.

Dependencies/integration: selective backup harness, timestamped history store, fast truncate, backup restore target filtering, statistics, and metadata verification.

Risks/test signals: failure is no fast truncate or metadata verification error. The large data volume is intended to produce HS content reliably.
