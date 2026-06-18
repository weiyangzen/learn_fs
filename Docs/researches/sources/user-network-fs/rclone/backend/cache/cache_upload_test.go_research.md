# sources/user-network-fs/rclone/backend/cache/cache_upload_test.go

## Purpose
This test file targets the cache backend's temporary upload queue. It verifies that writes can land in a local temp filesystem, appear through cache immediately, then move asynchronously to the wrapped remote.

## Important APIs, Types, And Control Flow
Tests create cache filesystems with `tmp_upload_path` and `tmp_wait_time`, then use `runInstance` helpers from `cache_internal_test.go`. `testInternalUploadQueueOneFile` writes a large file, checks it exists in temp storage, waits for background upload notifications, verifies temp deletion, and reads from the final remote. Other tests cover temp-dir creation, queue persistence/reconciliation across restarts, moving existing files, temp path cleanup, multiple queued files, and operations on temp or already-uploading files.

## State And Persistence
State spans the temp upload directory, the persistent Bolt `pending` bucket, object metadata in the cache DB, and eventual files on the wrapped remote. Tests use `PurgeTempUploads` and `SetPendingUploadToStarted` helper methods from `utils_test.go` to force queue states. For crypt-wrapped roots they compare adjusted encrypted file sizes and encrypted path names.

## Dependencies And Integration Points
The tests depend on `cache.Persistent` pending-upload APIs, background uploader notifications (`BackgroundUploadStarted`, `Completed`, `Error`), wrapped/local/temp filesystem move/copy/dir-move features, and `walk.ListR` behavior indirectly through backend operations.

## Risks And Test Signals
Important signals are queue-to-upload completion, temp objects overriding source listings, started uploads blocking move/delete/dir-move, allowed copies of uploading objects, update behavior on temp objects, cleanup of empty temp parent directories, and eventual absence of queued temp files. Risks include timing-sensitive waits, remote-specific feature availability, tests that branch around unsupported move/copy features, and commented FIXME coverage for updating an actively uploading file.
