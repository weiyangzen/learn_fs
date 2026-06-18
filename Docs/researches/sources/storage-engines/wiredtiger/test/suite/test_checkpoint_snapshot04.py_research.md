# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot04.py

Purpose: tests backup dump/comparison behavior when transaction IDs are written to disk and checkpoint snapshot state exists.

Important APIs and types: `backup_base`, backup cursor `open_cursor("backup:")`, optional backup `target=`, `compare_backups`, `SimpleDataSet`, and transaction-per-row updates.

Control flow: start an uncommitted insert beyond the main range, write committed data in many transactions, checkpoint, create a full or targeted backup by copying backup cursor files, rollback the uncommitted transaction, then compare backup contents against the original twice.

State and persistence behavior: backup must represent the checkpointed state consistently even with transaction IDs on disk and an active transaction. Targeted backup lacks history store, so the second compare checks that RTS does not change backup contents on repeat.

Dependencies and integration points: integrates backup cursor file lists, dataset verification, and backup comparison utilities. Scenarios cover row-string and column stores plus full/targeted backup.

Risks: relies on filesystem copy of backup cursor entries. It does not explicitly inspect RTS stats, using compare output as the persistence signal.

Test signals: `compare_backups` succeeds for the backup versus the live home on repeated attempts.
