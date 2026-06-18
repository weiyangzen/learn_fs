# sources/storage-engines/wiredtiger/test/suite/test_live_restore06.py

## Purpose
Ensures backups taken from live restore destinations clean `nbits=-1` metadata and produce reusable backup metadata with `nbits=0`.

## APIs, Types, And Functions
Defines `test_live_restore06` extending `backup_base`. It uses `SimpleDataSet`, live restore statistics, file manager close settings, timing stress `live_restore_clean_up`, backup cursors, and metadata cursors.

## Control Flow, State, And Persistence
The test creates three source files, backs up to `SOURCE`, opens `DEST` with one live restore thread and aggressive sweep settings, loops until `WT_LIVE_RESTORE_COMPLETE`, then verifies destination metadata includes `nbits=-1` for files. It then runs `do_backup_test` twice, once from complete live restore mode and once from non-live restore mode, checking `WiredTiger.backup` omits `nbits=-1` and reopened backup metadata contains `nbits=0`.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore cleanup, sweep timing, backup metadata export, and restart. Risks are leaking placeholder allocation metadata into backups or reopening backups with live restore-only metadata. Signals are completion state, metadata string assertions, and successful backup reopen.
