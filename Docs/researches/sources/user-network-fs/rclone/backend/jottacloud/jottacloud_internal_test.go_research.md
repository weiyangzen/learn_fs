
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud_internal_test.go

## Purpose
Provides package-internal tests for Jottacloud helper behavior and backend-specific fstests extension hooks.

## Important APIs, Types, And Control Flow
`TestReadMD5` iterates sizes and memory thresholds, computes the expected MD5 from `readers.NewPatternReader`, calls `readMD5`, and verifies both returned checksum and replay reader contents. `InternalTestMetadata` uploads an object with `btime` and `mtime` metadata through `fstests.PutTestContentsMetadata`, reads back `Object.Metadata`, and checks timestamp precision, upload time, and content type where relevant. `InternalTest` exposes this as `fstests.InternalTester`.

## State And Persistence
The test creates temporary remote objects under the configured Jottacloud test remote and removes them afterward. `TestReadMD5` exercises both in-memory and temporary-file buffering without permanent repository state.

## Dependencies And Integration Points
Uses rclone `fstest`, `fstests`, `fs.Metadata`, random test contents, pattern readers, and testify assertions. It integrates with the generic backend integration suite through the `InternalTester` interface.

## Risks And Test Signals
Signals checksum correctness across threshold branches and verifies metadata round-trip behavior. Remaining risk is that remote metadata tests require a live account and can be sensitive to server timestamp precision or upload-time delays.
