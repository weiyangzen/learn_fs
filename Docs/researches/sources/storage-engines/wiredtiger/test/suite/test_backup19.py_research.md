# sources/storage-engines/wiredtiger/test/suite/test_backup19.py

Purpose: focused block incremental backup test where later incremental backup is driven by source identifier state maintained by the helper. It resembles a shorter version of the complex-data/hotspot path.

Important APIs are custom `add_complex_data`, `take_full_backup`, `take_incr_backup`, `compare_backups`, checkpoints, and directory setup. Control flow switches home to `WT_BLOCK`, creates `table:main`, initializes full and incremental backup directories, writes initial data, takes a full backup into incremental home, checkpoints, writes more complex data, checkpoints again, takes a separate full backup, then takes an incremental backup and compares. State behavior is incremental block tracking across one source-to-current generation. Risks include reliance on `backup_base` defaults for source-only incremental ID handling and class-level counters. Test signal is full/incremental backup equivalence for the main table.
