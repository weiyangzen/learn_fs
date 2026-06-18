# sources/storage-engines/wiredtiger/test/suite/test_compact10.py

Purpose: verifies background compaction does not alter logical table contents by comparing full backups taken before and after compaction.

Important APIs and types: `backup_base`, `compact_util`, `take_full_backup`, `compare_backups`, `turn_on_bg_compact`, `get_bg_compaction_success`, and `get_bytes_recovered`.

Control flow: generate five tables, populate, checkpoint, delete half the rows, checkpoint, take full backup 1, run background compaction once with `free_space_target=1MB`, wait until all tables are processed and bytes recovered is positive, take full backup 2, then compare all table backups.

State and persistence behavior: compaction rewrites/reclaims blocks but must preserve table content. Backup comparison acts as a logical consistency check across compacted and uncompacted file layouts.

Dependencies and integration points: full backup support, background compaction, compact utility data population/deletion, and backup comparison. Tiered hook is skipped because both compaction and backup are unsupported/unsuitable.

Risks: waits on asynchronous background success count. Backup comparison must normalize physical differences or compare logical dumps as implemented by `backup_base`.

Test signals: bytes recovered is positive and every URI compares equal between pre- and post-compaction backups.
