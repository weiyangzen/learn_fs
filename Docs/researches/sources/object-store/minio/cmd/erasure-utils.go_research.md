<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-utils.go -->
# sources/object-store/minio/cmd/erasure-utils.go

## Purpose
Small erasure-coding helper layer for reconstructing contiguous data from encoded shards and extracting deployment IDs embedded in multipart upload IDs for site-replication forwarding.

## Important APIs, types, and functions
- `getDataBlockLen` totals data-shard lengths across the first `dataBlocks` entries.
- `writeDataBlocks` writes a requested range from data shards to an `io.Writer`, honoring offset and length across shard boundaries.
- `getDeplIDFromUpload` decodes a base64 raw URL upload ID and returns the prefix before the first dot.

## Control flow
`writeDataBlocks` rejects negative offset/length, checks shard count and available data length, skips whole shards until the requested offset is reached, then writes either the remaining full shard or the final truncated slice. `getDeplIDFromUpload` decodes the upload ID, splits at the first dot, and returns an error if the encoded value is malformed.

## State and persistence behavior
The file has no persistent state. Its output is derived entirely from in-memory shard slices or a request upload ID. `writeDataBlocks` accepts a context but does not currently test it inside the loop, so cancellation must be handled by the writer or caller.

## Dependencies and integration points
`writeDataBlocks` returns Reed-Solomon errors used by erasure decode paths and is consumed by tests in `erasure_test.go`. `getDeplIDFromUpload` is used by upload forwarding middleware to route multipart operations to the peer deployment that initiated the upload.

## Risks and edge cases
Range math must stay correct across uneven shard sizes, short data, and partial final writes. `writeDataBlocks` increments by bytes reported by the writer but does not verify full writes without error. Upload ID parsing assumes deployment ID and upload suffix are dot-separated after raw URL base64 decoding.

## Test signals
`TestErasureEncodeDecode` reconstructs shards and calls `writeDataBlocks` to compare decoded bytes with original random data. Upload ID parsing is indirectly covered through site-replication upload forwarding behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-utils.go -->
