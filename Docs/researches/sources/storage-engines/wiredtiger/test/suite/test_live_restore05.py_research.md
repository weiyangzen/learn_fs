# sources/storage-engines/wiredtiger/test/suite/test_live_restore05.py

## Purpose
Reproduces and guards against duplicate `live_restore=` metadata entries in a live restore home.

## APIs, Types, And Functions
Defines `test_live_restore05` extending `backup_base`, with row-integer and column-store scenarios. It uses `SimpleDataSet`, `take_full_backup`, `open_conn` with `live_restore`, and `runWt` to dump `file:WiredTiger.wt`.

## Control Flow, State, And Persistence
The test creates one collection, checkpoints, backs up to `SOURCE`, removes home files, opens `DEST` with live restore and no background migration threads, dumps the metadata file through `wt -l SOURCE`, and scans the dump text. For each metadata line containing `live_restore=`, it asserts there is not another occurrence later in the same line.

## Dependencies, Integration, Risks, And Test Signals
Depends on metadata rewrite behavior during live restore and utility dump output. The risk is repeated config insertion causing malformed or ambiguous metadata. The signal is textual absence of duplicate `live_restore=` substrings in dumped `WiredTiger.wt` metadata.
