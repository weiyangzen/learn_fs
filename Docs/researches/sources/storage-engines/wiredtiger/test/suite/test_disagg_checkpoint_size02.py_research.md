# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size02.py

Purpose: tests database-level `database_size=` stored in disaggregated checkpoint completion records.

Important APIs and control flow: `get_database_size` parses `disagg_get_complete_checkpoint_meta()`. Tests cover no completed checkpoint error, initial table checkpoint, size increases with inserts, size decreases after removing most rows, similar deltas across multiple btrees, restart preservation, and crash behavior through `simulate_crash_restart`.

State and persistence: size lives in complete checkpoint metadata rather than individual stable file metadata. `disagg_size_buffer` accounts for the 1 MB buffer included for new databases.

Dependencies and integration: uses `@disagg_test_class`, `wiredtiger.WiredTigerError`, layered tables, checkpoint metadata helpers, and crash/restart helper.

Risks and test signals: assertions compare monotonic growth, reduction after truncation, approximate restart equality, and no change after an uncheckpointed crash. Failures point at checkpoint completion accounting or crash recovery.
