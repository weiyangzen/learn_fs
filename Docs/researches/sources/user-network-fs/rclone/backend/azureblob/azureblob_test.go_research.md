# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_test.go

## Purpose
This file wires the Azure Blob backend into rclone's generic filesystem integration test suite and adds a focused unit test for access tier validation. It also exposes test-only setters used by fstests to tune chunk size and copy cutoff.

## Important APIs, Types, and Functions
- `TestIntegration` runs `fstests.Run` against `TestAzureBlob:` with tier tests for Hot, Cool, and Cold, chunked upload enabled, and `use_copy_blob=false`.
- `TestIntegration2` runs the same generic suite with `directory_markers=true` unless an explicit remote is supplied.
- `(*Fs).SetUploadChunkSize` and `(*Fs).SetCopyCutoff` adapt private setters to fstests interfaces.
- Interface assertions ensure `Fs` satisfies `fstests.SetUploadChunkSizer` and `fstests.SetCopyCutoffer`.
- `TestValidateAccessTier` validates case-insensitive accepted tiers and rejection of empty/unknown values.

## Control Flow
Both integration tests delegate broad behavior to `fstests.Run`, which exercises object create/read/update/delete, listing, copy/move capabilities where advertised, hashes, modtimes, and optional internal tests. The second test skips when `-remote` is provided to avoid unexpected config mutation and specifically validates directory marker mode. The access tier test iterates a table of tier strings through `validateAccessTier`.

## State and Persistence Behavior
The integration tests create and remove containers/blobs in the configured Azure test remote. Extra config changes are scoped through fstests. The setter methods mutate `f.opt.ChunkSize` and `f.opt.CopyCutoff` during tests and return old values for restoration.

## Dependencies and Integration Points
The file depends on rclone `fs`, `fstest`, and `fstests`, plus `testify/assert`. It is the public test entry point that indirectly triggers `Fs.InternalTest` from `azureblob_internal_test.go`.

## Risks and Edge Cases
- Live Azure credentials and remote naming are required for full coverage.
- `use_copy_blob=false` biases tests toward multipart/server-side copy behavior and may not fully cover same-account Copy Blob defaults.
- `TestIntegration2` is skipped under explicit `-remote`, so directory marker coverage can be absent in custom test runs.
- The access tier unit test does not include all behavior around archive tier update/delete, only validation.

## Test Signals
The file verifies broad conformance to rclone's filesystem contract, chunked upload tunability, tier feature expectations, and access-tier input validation.
