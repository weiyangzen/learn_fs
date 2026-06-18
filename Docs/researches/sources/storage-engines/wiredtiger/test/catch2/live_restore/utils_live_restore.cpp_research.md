# sources/storage-engines/wiredtiger/test/catch2/live_restore/utils_live_restore.cpp

## Purpose
Implements small live-restore test utilities for opening live-restore file handles and creating test files with controlled contents.

## Important APIs, Types, And Functions
`open_lr_fh` verifies the supplied destination path starts with `env.DB_DEST`, then calls `WTI_LIVE_RESTORE_FS::iface.fs_open_file` with data-file type and optional flags. `create_file` asserts the path does not already exist, writes `len` copies of `fill_char` using `std::ofstream`, and closes the stream.

## Control Flow
Both helpers are straight-line wrappers. `open_lr_fh` derives file-system/session pointers from `live_restore_test_env`; `create_file` builds a string and writes it.

## State And Persistence Behavior
`open_lr_fh` returns a live-restore handle without closing it. `create_file` writes real files in source or destination directories for tests.

## Dependencies And Integration Points
Depends on `utils_live_restore.h`, `live_restore_test_env`, `testutil_exists`, and live-restore file-system open behavior.

## Risks And Edge Cases
`open_lr_fh` guards against accidentally opening a source path through the live destination API. `create_file` refuses overwriting existing files, so tests must remove stale artifacts explicitly.

## Test Signals
Failures are expressed through Catch2 `REQUIRE` in helper assertions or returned file-open status checked by callers.
