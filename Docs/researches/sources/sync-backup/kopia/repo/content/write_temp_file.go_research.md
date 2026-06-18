# sources/sync-backup/kopia/repo/content/write_temp_file.go

## Purpose
Provides a helper for writing temporary files atomically and durably enough for later rename/use by content code. It creates a temporary file in a target directory, writes bytes, syncs the file, and cleans up on any failure.

## Important APIs, Types, And Functions
Private interfaces `file` and `fsInterface` abstract file operations for testing. `localFS` adapts `os.CreateTemp`, `os.Remove`, and `os.MkdirAll`. Public-within-package functions are `writeTempFileAtomic` and `writeTempFileAtomicImp`.

## Control Flow
`writeTempFileAtomicImp` attempts `CreateTemp`; if the directory is missing, it creates the directory with `cache.DirMode` and retries. It defers file close and, if any error occurred, removes the temporary file and clears the returned name. It writes all data, calls `Sync`, and returns the temp filename without renaming it.

## State And Persistence
The only persistent side effect is a synced temp file under the requested directory on success. On write, sync, close, or cleanup errors, it returns joined errors and removes the temp file when possible.

## Dependencies And Integration Points
Depends on `os`, `io`, `io/fs`, `errors.Join`, `pkg/errors`, and `internal/cache` for directory mode. It is intended for code that needs to stage a file before an atomic rename.

## Risks And Edge Cases
The function name says atomic, but this helper only atomically creates a temp file; callers must perform any final rename themselves. It does not retry short writes because `Write` returning `n < len(data), nil` is not handled. Close errors are joined after success and force cleanup, which is conservative but can surprise callers if data was written and synced.

## Test Signals
`write_temp_file_test.go` covers successful writes, empty data, missing directory creation, unwritable directory, sync invocation, no leaked temp files on success, and cleanup on write/sync/close errors.
