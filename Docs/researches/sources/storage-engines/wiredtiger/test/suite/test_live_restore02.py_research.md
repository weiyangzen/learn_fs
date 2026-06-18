# sources/storage-engines/wiredtiger/test/suite/test_live_restore02.py

## Purpose
Exercises live restore background migration until completion while source collections are compared with the destination.

## APIs, Types, And Functions
Defines `test_live_restore02` extending `backup_base`, with scenarios over key format and `read_size`. It uses `SimpleDataSet`, `take_full_backup`, `open_conn` with `live_restore`, `statistics:` cursor for `live_restore_state`, and `WT_LIVE_RESTORE_COMPLETE`.

## Control Flow, State, And Persistence
The test populates three files, checkpoints, backs up to `SOURCE`, deletes local home files, opens `DEST` with one live restore thread, and loops for up to 120 seconds. During the loop it creates extra files to stress file creation while migration runs. After completion, it opens `SOURCE` separately and compares every key/value in the restored URIs. It also asserts no `.stop` files remain.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore support, verbose progress logs, statistics, and backup correctness. Risks are migration stalls, file-create assertions during restore, partial data copy, and leaked stop markers. Signals are completion state, row-by-row equality against `SOURCE`, and absence of stop files.
