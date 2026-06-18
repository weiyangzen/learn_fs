# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot06.py

Purpose: tests recovery/backup correctness when checkpoint runs concurrently with truncates, reinserts, and eviction across two tables.

Important APIs and types: `backup_base`, `checkpoint_thread`, `copy_wiredtiger_home`, `simulate_crash_restart`, `take_full_backup`, truncate APIs, and `debug=(release_evict)` eviction cursors.

Control flow: create two logged tables, populate and verify both, remove key 50, start a truncate transaction deleting range 1-100, start another transaction reinserting key 50 with `valueb`, run checkpoint and wait for snapshot acquisition, commit insert then truncate, evict table 1 changes, checkpoint again, then backup or crash restart and verify both tables.

State and persistence behavior: out-of-order commit between insert and truncate plus eviction can create inconsistent checkpoint state. Recovery/backup should preserve the final reinserted key in both tables.

Dependencies and integration points: logging, checkpoint timing stress, backup/crash paths, and duplicate copy of pre-restart home for diagnostics.

Risks: no direct RTS stat assertions; correctness is key-based. Concurrent timing is central and uses polling on checkpoint snapshot acquisition.

Test signals: after restart/restore, key 50 is found in both tables with `valueb`.
