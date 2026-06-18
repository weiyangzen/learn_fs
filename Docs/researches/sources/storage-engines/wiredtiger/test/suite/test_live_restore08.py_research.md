# sources/storage-engines/wiredtiger/test/suite/test_live_restore08.py

## Purpose
Tests that bulk cursor usage is disallowed on files migrated by live restore after restore completion.

## APIs, Types, And Functions
Defines `test_live_restore08` extending `backup_base`. Helpers read `live_restore_state`, wait for completion, and populate a backup containing a normal file and an empty `file:bulk`. It uses `open_cursor(..., "bulk")` for the final error assertion.

## Control Flow, State, And Persistence
The test creates `SOURCE` with one populated file and one newly created bulk target, opens `DEST` with one live restore thread and small read size, waits until `WT_LIVE_RESTORE_COMPLETE`, then attempts to open a bulk cursor on the migrated `file:bulk`. Since the object is no longer newly created in the destination, bulk load must be rejected.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore migration state and bulk cursor eligibility rules. Risks include allowing bulk load to overwrite restored objects or classifying migrated empty files as new objects. Test signal is the expected `bulk-load is only supported on newly created objects` error.
