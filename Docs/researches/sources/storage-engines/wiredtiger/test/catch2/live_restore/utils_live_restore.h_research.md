# sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.h

## Purpose
Declares live-restore test enums and helper functions shared by API and unit tests.

## Important APIs, Types, And Functions
Defines `HasDest`, `HasSource`, `IsMigrating`, and `HasStop` enums for permutation tests. Declares `create_file` and `open_lr_fh`.

## Control Flow
The header contains declarations only. Test files include it to share consistent setup vocabulary and helper APIs.

## State And Persistence Behavior
The enums model persistent file-system state combinations; helper declarations operate on real source/destination files through the implementation file.

## Dependencies And Integration Points
Includes `<string>` and `live_restore_test_env.h`, so it also exposes live-restore internals to tests.

## Risks And Edge Cases
Because helpers use fixed enum names like `DEST`, `SOURCE`, and `STOP`, the header is convenient but broad in namespace scope within `utils`. Future tests should avoid ambiguous imports.

## Test Signals
No direct tests; correctness is indirect through all live-restore API/unit tests that compile and use these declarations.
