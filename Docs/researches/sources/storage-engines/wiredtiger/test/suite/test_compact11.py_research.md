# sources/storage-engines/wiredtiger/test/suite/test_compact11.py

Purpose: verifies background compaction does not incorrectly clear incremental backup block modification bits while compacting tables.

Important APIs and types: `backup_base`, `compact_util`, metadata cursor parsing of `blocks=...`, `take_full_backup`, `take_incr_backup`, `compare_backups`, and `turn_on_bg_compact`.

Control flow: create five tables, populate first half, checkpoint, take initial full backup for incremental chain, populate second half, checkpoint, delete half, checkpoint, take a reference full backup, parse block modification bitmaps, run background compaction once, and whenever recovered bytes changes take an incremental backup. Then compare each incremental backup against the reference full backup.

State and persistence behavior: compaction modifies blocks physically but must preserve incremental backup metadata so incremental backups remain logically complete.

Dependencies and integration points: backup ID management from `backup_base`, metadata block bitmap format, background compaction, and filesystem copy of backup homes.

Risks: `parse_blkmods` records bitmaps but the stored values are not asserted later. The test depends on bytes-recovered changes to trigger incremental backups.

Test signals: bytes recovered becomes positive and every incremental backup generated during compaction compares equal to the full reference for each URI.
