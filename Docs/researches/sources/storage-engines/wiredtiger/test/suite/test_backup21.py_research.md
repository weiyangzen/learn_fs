# sources/storage-engines/wiredtiger/test/suite/test_backup21.py

Purpose: tests create/drop operations racing with full backup cursors. It validates snapshot semantics: newly created tables after cursor open are not in backup, while tables dropped after cursor open remain listed.

Important APIs are `op_thread`, `queue.Queue`, `threading.Event`, `session.open_cursor('backup:')`, `take_full_backup`, and helper `add_data`. Control flow creates and populates a base table, starts an operation thread, then for 50 iterations opens a backup cursor, queues a create or drop operation, copies full backup files, and checks file list membership. At midpoint it drains creates before switching to drops. State behavior is schema metadata as seen by a backup cursor versus concurrent mutations. Risks include queue timing, file naming assumptions, and backup directory reuse. Test signals are file-list assertions for new/dropped tables and clean thread shutdown.
