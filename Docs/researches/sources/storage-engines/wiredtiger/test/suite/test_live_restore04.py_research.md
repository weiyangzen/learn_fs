# sources/storage-engines/wiredtiger/test/suite/test_live_restore04.py

## Purpose
Tests `wt` utility behavior against an unfinished live restore home, including dump, verify, printlog, and error handling without a live restore source path.

## APIs, Types, And Functions
Defines `test_live_restore04` extending `backup_base`, with column and row-integer scenarios. It uses `runWt`, `SimpleDataSet`, `take_full_backup`, `filecmp.cmp`, and the utility `-l SOURCE` live restore option.

## Control Flow, State, And Persistence
The test creates three logged files, dumps original utility output, backs up to `SOURCE`, removes home files except `SOURCE` and utility output, opens and closes a `threads_max=0` live restore connection to leave migration incomplete, then runs `wt dump` without `-l` expecting an error. It runs `wt -l SOURCE printlog`, then dumps and verifies each file through live restore and compares dumps to originals.

## Dependencies, Integration, Risks, And Test Signals
Depends on Unix live restore, the external `wt` utility, logged homes, and backup layout. Risks are utility commands bypassing live restore rules, failing to read source-backed files, or mismatched dump output. Signals are non-empty error/printlog files, successful dump/verify, and byte-identical dump comparisons.
