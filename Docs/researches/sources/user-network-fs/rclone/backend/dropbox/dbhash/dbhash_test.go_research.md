# sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash_test.go

## Purpose
This file tests the Dropbox content hash implementation against known expected hashes, different caller write chunk sizes, boundary lengths, and selected API behavior.

## Important APIs, types, and functions
- `testChunk` streams repeated `A` bytes into `dbhash.New()` using a caller-selected chunk size and checks expected hex digests for lengths from zero through 8 MiB plus one.
- `TestHashChunk16M`, `TestHashChunk8M`, `TestHashChunk4M`, `TestHashChunk2M`, `TestHashChunk1M`, `TestHashChunk64k`, `TestHashChunk32k`, `TestHashChunk2048`, and `TestHashChunk2047` run the same expected-length matrix with different write sizes.
- `TestSumCalledTwice` verifies allowed and disallowed `Sum` call ordering.
- `TestSize`, `TestBlockSize`, and `TestSum` verify API dimensions and package-level checksum output.

## Control flow
For each write chunk size, the helper allocates a chunk of `A` bytes, writes whole chunks until less than one chunk remains, writes the remainder, calls `Sum(nil)`, hex encodes it, and compares against the expected digest for that total length. Boundary lengths include one less than, exactly, and one greater than 4 MiB and 8 MiB.

## State and persistence behavior
Tests are pure in-memory checks. They exercise digest internal state transitions indirectly through writes, sums, resets, and panic assertions.

## Dependencies and integration points
The file imports the public `dbhash` package and testify assertions. It validates `dbhash.go` independently of the rest of the Dropbox backend.

## Risks and edge cases
- The `fmt.Sprintf` message currently reports `n` from the final write rather than the total tested length; this affects failure diagnostics only.
- `TestSum` expects the fixed array shape returned by `dbhash.Sum`, including implicit trailing zero bytes because the array length is 64 while the actual digest is 32 bytes.
- The tests cover many boundary and chunking combinations but do not test random data or interleaved `Reset` after partial writes beyond the `Sum` call-order case.

## Test signals
The expected hashes give strong regression coverage for the Dropbox algorithm, especially block-boundary handling and write chunk independence. The panic test codifies the implementation's nonstandard `Sum` state behavior.
