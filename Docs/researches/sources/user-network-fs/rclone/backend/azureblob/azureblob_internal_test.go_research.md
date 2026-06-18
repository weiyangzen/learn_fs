# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_internal_test.go

## Purpose
This file provides Azure Blob backend internal integration tests that go beyond generic fstests. It exercises implementation-specific block ID generation, feature flags, uncommitted block recovery, gzip content-encoding behavior, and metadata/header/tag mapping across upload and server-side copy paths.

## Important APIs, Types, and Functions
- `TestBlockIDCreator` validates `newBlockIDCreator`, `newBlockID`, and `checkID`.
- `(*Fs).testFeatures` checks that `SetTier` and `GetTier` feature flags are enabled.
- `ReadSeekCloser` adapts a `strings.Reader` for direct SDK `StageBlock`.
- `stageBlockWithoutCommit` creates remote uncommitted block state without committing a blob.
- `testWriteUncommittedBlocks` forces multipart upload/copy over existing uncommitted block IDs.
- `gz` and `md5sum` support gzip behavior checks.
- `testGzipEncoding` verifies compressed-object reads with and without backend decompression.
- `InternalTest` registers internal subtests for fstests.
- `getProps`, `assertHeadersAndMetadata`, and `getTagsMap` inspect Azure properties and tags through SDK calls.
- `testMetadataPaths` covers metadata mapping for single-part/multipart uploads and copies.

## Control Flow
The block ID test uses deterministic random bytes after checking randomness is nonzero and distinct. The uncommitted block test stages uncommitted data, confirms no object exists, uploads a multi-chunk object over that path, then stages another path and copies over it to confirm cleanup/retry behavior. Metadata tests create source objects with `fstests.PutTestContentsMetadata`, use rclone config contexts with `Metadata` and `MetadataSet`, perform uploads or `f.Copy`, then read raw blob properties and tags to assert Azure headers/user metadata/tags. The invalid tag subtest builds a static object with malformed `x-ms-tags` and expects `Put` to fail.

## State and Persistence Behavior
These tests mutate live Azure containers by creating blobs, uncommitted blocks, tags, headers, and copied objects, with most subtests deferring object removal. `testWriteUncommittedBlocks` intentionally creates transient uncommitted block state to exercise production cleanup. `testGzipEncoding` toggles `f.opt.Decompress` within a subtest and restores it.

## Dependencies and Integration Points
The tests use Azure SDK `blob` and `blockblob` clients directly, rclone `fstests`, `fstest` items, random data generation, object metadata helpers, and `testify` assertions. They rely on a configured live Azure Blob test remote and are integrated through the backend's `InternalTest` hook.

## Risks and Edge Cases
- Tests are integration-heavy and depend on service credentials, network behavior, and Azure support for tags/tier operations.
- `testing.Short()` skips the metadata-path suite, so fast test runs miss much of the metadata regression coverage.
- The uncommitted block test manipulates remote state that can linger if cleanup fails before deferred removal.
- Gzip tests validate a compressed payload path where `Size()` and `Hash()` intentionally become unknown under decompression.
- Metadata tests assume Azure service casing/behavior for headers and tags while normalizing user metadata keys.

## Test Signals
This file itself is the primary signal for several tricky backend behaviors: random block IDs, uncommitted block repair, gzip accept/decompress semantics, metadata mapper integration, copy metadata fallback, tag parsing, and tier feature advertisement.
