# sources/storage-engines/wiredtiger/test/catch2/live_restore/live_restore_test_env.h

## Purpose
Declares the reusable live-restore test environment class and includes the C/C++ dependencies needed by live-restore Catch2 tests.

## Important APIs, Types, And Functions
`utils::live_restore_test_env` exposes constants `DB_DEST` and `DB_SOURCE`, members `WTI_LIVE_RESTORE_FS *lr_fs`, `std::unique_ptr<connection_wrapper> conn`, and `WT_SESSION_IMPL *session`, plus constructor and path helper methods.

## Control Flow
The header has no runtime control flow beyond class declaration. Test files include it directly or through `utils_live_restore.h` and construct the environment at section or test scope.

## State And Persistence Behavior
The declared class owns a WiredTiger connection wrapper and session pointer and references the live-restore file system for the connection. Path helpers model persistent backing files in destination/source directories.

## Dependencies And Integration Points
Includes Catch2, shared test utilities, `wt_internal.h`, `test_util.h`, `live_restore_private.h`, and `connection_wrapper`. It bridges C live-restore internals into C++ Catch2 tests.

## Risks And Edge Cases
The header exposes raw internal pointers for tests to mutate, which is intentional but can bypass production invariants. Include order matters because it pulls internal C headers inside `extern "C"`.

## Test Signals
No direct tests exist for the header alone; all live-restore tests validate it by constructing `live_restore_test_env` and using its members.
