# sources/sync-backup/kopia/internal/dirutil/mssubdirall_test.go

Purpose: tests `MkSubdirAll` behavior with a small OS abstraction wrapper around real filesystem calls.

Important APIs/types/functions: `testOSI`, `TestMkSubdirAll`, `testutil.TempDirectory`, and `dirutil.ErrTopLevelDirectoryNotFound`.

Control flow: ordered cases check rejecting creation at or above top-level, creating one subdirectory, creating nested subdirectories, accepting existing directories, then injecting a generic mkdir error and requiring it to propagate.

State and persistence behavior: creates directories inside a temporary test directory; no state survives the test.

Dependencies/integration: uses real `os.Mkdir`, `os.IsExist`, `os.IsNotExist`, path separators, `filepath.Join`, and `testify/require`.

Risks/test signals: filename appears as `mssubdirall_test.go`, likely a typo relative to `mksubdirall.go`, but package tests still run. Tests do not cover trailing separators, relative path traversal, or symlink behavior.
