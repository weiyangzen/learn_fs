# sources/user-network-fs/rclone/backend/cache/utils_test.go

## Purpose
This test-only file exposes small helpers on `Persistent` so cache upload tests can force pending-upload queue states.

## Important APIs, Types, And Control Flow
`PurgeTempUploads` deletes and recreates the pending upload bucket under the persistent DB while holding `tempQueueMux`. `SetPendingUploadToStarted` calls `updatePendingUpload` and sets the internal `Started` flag to true for a remote.

## State And Persistence
Both helpers mutate the Bolt `pending` bucket and are compiled only for `!plan9 && !js`. They do not touch temp filesystem files, so tests must keep DB and temp FS state coherent.

## Dependencies And Integration Points
The helpers depend on unexported package internals because this file is in package `cache`, not `cache_test`. They are consumed by `cache_upload_test.go` to isolate temp-file and uploading-file operation scenarios.

## Risks And Test Signals
Risk is that tests can create states not reachable through normal APIs, especially marking entries started without a live background upload. This is intentional for negative-path coverage around move/delete/update blockers.
