# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot05.py

Purpose: tests backup recovery after an inconsistent checkpoint created following a bulk load and concurrent checkpoint/transaction/eviction sequence.

Important APIs and types: `backup_base`, bulk cursor, `checkpoint_thread`, `wttest.open_cursor`, `stat.conn.checkpoint_snapshot_acquired`, `take_full_backup`, and RTS stats.

Control flow: bulk-load rows with `valuea`, hold a transaction updating all rows to `valueb`, start a single checkpoint thread and wait for snapshot acquisition, commit the update, evict all pages to force inconsistent checkpoint content, take a full backup, reopen the backup, and verify contents.

State and persistence behavior: recovery of the backup is expected to fix inconsistent checkpoint state and retain checkpointed bulk-loaded values, not the concurrent updated values.

Dependencies and integration points: logging enabled at connection level but table config disables logging for bulk data; timing stress slows checkpoint. Disaggregated is skipped for bulk-load support.

Risks: uses an `assert` for checkpoint count/skipped stats rather than `self.assert*`, making it dependent on Python assertion settings. Timing loop is deliberately aggressive.

Test signals: backup restore reads all `valuea` rows, `txn_rts_inconsistent_ckpt` is positive, and `txn_rts_keys_removed` equals zero.
