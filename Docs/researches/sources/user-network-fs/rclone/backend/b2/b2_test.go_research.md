# sources/user-network-fs/rclone/backend/b2/b2_test.go

## Purpose
Top-level B2 integration test wiring for rclone's generic filesystem test suite plus test-only upload/copy cutoff setters.

## Important APIs, types, and functions
`TestIntegration` runs `fstests.Run` against `TestB2:` with nil `*Object` and chunked upload config requiring `minChunkSize` and multiple chunks. `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` expose unexported setters to fstests. Interface assertions document the setter contracts.

## Control flow
The generic test harness creates, lists, updates, copies, moves, and deletes data on the configured real B2 remote. Setter methods allow tests to force multipart upload/copy paths without exporting production APIs.

## State and persistence
No local state beyond in-memory option mutations during tests. Test execution persists temporary objects in the configured B2 test remote.

## Dependencies and integration points
Depends on rclone `fstests` and `fs.SizeSuffix`, and on package-local B2 constants/types.

## Risks
Requires an externally configured `TestB2:` remote and can be affected by account permissions, B2 rate limits, eventual consistency, and bucket lifecycle settings.

## Test signals
Passing this file signals the backend satisfies rclone's generic Fs/Object contract, including chunked upload behavior tuned through the setter interfaces.
