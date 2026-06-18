# sources/user-network-fs/rclone/lib/file/file_test.go

Source read signal: reviewed complete local file (170 lines, sha256 4e7f3eb1e7066ecf).

Purpose: Smoke-tests cross-platform file wrapper behavior and Windows reserved-name validation.

Important APIs/types/functions: Helpers `checkListingNoSize`, `checkListing`; tests `TestOpenFileRename`, `TestOpenFileDelete`, `TestOpenFileOperations`, and `TestIsReserved`.

Control flow: Tests create temp files with `Create`/`OpenFile`/`Open`, write and read data, remove or rename while the file handle remains open, and check directory listings. `TestIsReserved` skips non-Windows and validates reserved DOS names and trailing period/space.

State and persistence behavior: Uses `t.TempDir`, creates/removes files, and relies on cleanup after test completion.

Dependencies and integration points: Uses `os`, `path`, `runtime`, `io`, and `testify`. It validates the platform-specific `file_windows.go` sharing behavior through the common API.

Risks and test signals: Rename/delete semantics differ by OS; the tests express the intended Windows-compatible behavior. The reserved-name test only runs on Windows, leaving non-Windows no-op behavior implicit.
