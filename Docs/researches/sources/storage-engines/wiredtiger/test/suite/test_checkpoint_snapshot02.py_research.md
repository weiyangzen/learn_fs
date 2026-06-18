# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot02.py

Purpose: exercises inconsistent checkpoint recovery when a checkpoint takes its snapshot before a concurrent transaction commits, for both crash restart and backup restore paths, with and without timestamps.

Important APIs and types: `backup_base`, `checkpoint_thread`, `simulate_crash_restart`, `take_full_backup`, `stat.conn.checkpoint_snapshot_acquired`, RTS stats `txn_rts_inconsistent_ckpt` and `txn_rts_keys_removed`.

Control flow: helpers populate and verify data, start a checkpoint thread, wait until checkpoint snapshot is acquired, then commit a transaction. Test variants cover non-timestamped inserts, timestamped inserts beyond stable, and a mixed txnid/timestamp case with an extra rollback and second restart.

State and persistence behavior: checkpoint and eviction timing can leave inconsistent checkpoint state. Recovery or backup restore should roll back uncheckpointed effects and preserve only the last checkpointed stable contents.

Dependencies and integration points: logging is disabled for some datasets, timing stress slows checkpoint, and backup/crash paths share validation. Disaggregated is skipped; one variant skips tiered.

Risks: thread timing and polling of statistics are central. The `check` helper prints ordering diagnostics and accepts only exact target counts.

Test signals: table contains the expected checkpointed value after restore/restart; inconsistent checkpoint stat is positive; removed-key stat is non-negative and zero on the second restart path.
