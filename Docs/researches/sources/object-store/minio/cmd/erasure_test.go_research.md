<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure_test.go -->
# sources/object-store/minio/cmd/erasure_test.go

## Purpose
Tests Reed-Solomon erasure encode/decode behavior and provides a helper setup for filesystem-backed erasure tests. It validates that data and parity reconstruction produce original payload bytes under supported shard loss patterns.

## Important APIs, types, and functions
- `erasureEncodeDecodeTests` enumerates data/parity counts, missing shard counts, whether parity should be reconstructed, and expected failure.
- `TestErasureEncodeDecode` drives `NewErasure`, `EncodeData`, `DecodeDataAndParityBlocks`, `DecodeDataBlocks`, and `writeDataBlocks`.
- `erasureTestSetup` and `newErasureTestSetup` create temporary XL storage disks and a test bucket for later erasure tests.

## Control flow
The test fills a random 256-byte buffer, encodes it, nils selected data and parity shards, decodes with or without parity reconstruction, validates expected success/failure, checks reconstructed shard presence when successful, writes data shards back to a buffer, and compares with the original bytes.

## State and persistence behavior
The main test uses in-memory buffers. `newErasureTestSetup` creates filesystem-backed disks and a `testbucket` volume, returning paths and `StorageAPI` handles for callers to clean up.

## Dependencies and integration points
This test depends on MinIO's erasure implementation, Reed-Solomon semantics, random data generation, `writeDataBlocks` from `erasure-utils.go`, and XL storage test setup helpers.

## Risks and edge cases
The table covers several shard loss combinations but uses one small payload size. It verifies byte equality but not large-object block boundaries, checksums, writer short-write behavior, or context cancellation. Failure expectations encode erasure tolerance limits and will need updates if quorum/reconstruction policy changes.

## Test signals
Signals include expected decode errors for unrecoverable shard loss, non-nil reconstructed shards for successful cases, and exact decoded byte equality with original random data.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure_test.go -->
