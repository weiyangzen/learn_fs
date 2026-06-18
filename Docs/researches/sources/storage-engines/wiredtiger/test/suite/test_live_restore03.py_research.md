# sources/storage-engines/wiredtiger/test/suite/test_live_restore03.py

## Purpose
Checks that data-source file size statistics work for objects that still exist only in the live restore source directory.

## APIs, Types, And Functions
Defines `test_live_restore03` extending `backup_base`. It uses `SimpleDataSet`, backup creation, live restore with `threads_max=0`, and `statistics:<uri>` cursors with `statistics=(size)` to read `stat.dsrc.block_size`.

## Control Flow, State, And Persistence
The test creates one `file:` and one `table:` object, checkpoints, backs up to `SOURCE`, removes the original home files, opens `DEST` in live restore mode with no background threads, and queries block-size statistics for both URIs. Because no background migration is running, the statistics path must fetch size information through live restore's source-file view.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore and statistics size mode. Risks include returning zero or failing when metadata exists locally but the file has not migrated. Test signal is `block_size > 0` for both file and table URI statistics.
