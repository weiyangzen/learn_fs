# sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash_test.go

## Purpose
`mrhash_test.go` verifies the Mail.ru hash implementation across chunking strategies and size boundaries. It supplies known expected hex digests for empty, tiny, boundary, and multi-megabyte streams of repeated `A` bytes.

## Important APIs, Types, And Functions
The central helper is `testChunk(t, chunk int)`. It creates a reusable chunk buffer, writes each target length to a fresh `mrhash.New()` digest in the requested chunk size, and compares `hex.EncodeToString(d.Sum(nil))` against table-driven expected values. `TestHashChunk16M`, `TestHashChunk8M`, `TestHashChunk4M`, `TestHashChunk2M`, `TestHashChunk1M`, `TestHashChunk64k`, `TestHashChunk32k`, `TestHashChunk2048`, and `TestHashChunk2047` run the same vectors under different write boundaries. `TestSumCalledTwice`, `TestSize`, and `TestBlockSize` cover interface behavior.

## Control Flow
Each vector writes zero or more full chunks, then a final remainder. It calls `Sum(nil)` twice and expects identical output, which confirms that `Sum` does not mutate the digest state. The chunk sizes intentionally cross large Mail.ru upload-like boundaries and non-power-of-two boundaries.

## State And Persistence Behavior
The tests are pure in-memory unit tests. They allocate buffers up to 16 MiB and do not touch remote services or filesystem state.

## Dependencies And Integration Points
The file imports `backend/mailru/mrhash` and `testify/assert`. It provides the main direct safety net for the hash type registered by the Mail.ru backend.

## Risks And Edge Cases
The helper's failure message prints the final write length `n`, not the tested total length, which can make failed cases harder to diagnose. `TestSumCalledTwice` checks only that reset/sum does not panic; it does not assert the digest after reset, leaving the `small` slice reset behavior under-specified. `DecodeString` is not tested.

## Test Signals
Passing vectors signal correct small-file padding, length-suffixed SHA1 behavior above 20 bytes, chunk-boundary independence, and stable repeated `Sum`. Missing signals include reset correctness, bad hex handling, and comparison with live Mail.ru metadata.
