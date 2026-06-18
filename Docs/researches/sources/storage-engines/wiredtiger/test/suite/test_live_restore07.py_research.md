# sources/storage-engines/wiredtiger/test/suite/test_live_restore07.py

## Purpose
Checks that live restore from an empty source directory is rejected.

## APIs, Types, And Functions
Defines `test_live_restore07` with unused key-format scenarios. It uses `close_conn`, `os.mkdir`, `open_conn`, and `assertRaisesWithMessage` for `wiredtiger.WiredTigerError`.

## Control Flow, State, And Persistence
On non-Windows platforms, the test closes the default connection, creates empty `SOURCE` and `DEST` directories, then tries to open `DEST` with `live_restore=(enabled=true,path="SOURCE")`. No database state should be created through a successful restore because an empty source has no valid WiredTiger metadata to restore.

## Dependencies, Integration, Risks, And Test Signals
Depends on live restore startup validation and filesystem directory state. The risk is accepting an empty restore source and later failing with less clear metadata errors. The signal is the specific error message `Source directory is empty. Nothing to restore!`.
