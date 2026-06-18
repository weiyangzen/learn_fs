<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go

## Purpose
Tests the downloader orchestration package with a fake range-tracking item and a real remote test object.

## Important APIs, Types, and Functions
Defines `testItem` implementing downloader `Item` through `HasRange`, `FindMissing`, and `WriteAtNoOverwrite`. `TestDownloaders` contains `Download` and `EnsureDownloader` subtests.

## Control Flow
The test writes a large deterministic pattern object with `operations.RcatSize`, constructs a fresh `Downloaders` for each subtest, and closes it at the end. `Download` requests several sparse ranges and asserts they are present after the call returns. `EnsureDownloader` starts an async downloader and uses `assert.Eventually` until the requested range appears.

## State and Persistence Behavior
The fake item stores downloaded ranges in memory and verifies bytes against `readers.NewPatternReader` before marking ranges present. No cache files are written by this test; the source object is persisted to the `fstest` remote.

## Dependencies and Integration Points
Uses local backend import, `fstest`, `operations.RcatSize`, `ranges`, pattern readers, VFS default options, and the real downloader/chunked reader pipeline.

## Risks and Edge Cases
The fake `WriteAtNoOverwrite` reports no skipped bytes, so skip/stop behavior is not tested. Error handling, no-space handling, unknown-size rejection, downloader reuse windows, read-ahead expansion, and close-with-waiters are not deeply covered.

## Test Signals
Good signal for basic range download completion and byte correctness. Limited signal for failure and resource-management paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go -->
