# sources/user-network-fs/rclone/backend/dropbox/dbhash/dbhash.go

## Purpose
`dbhash.go` implements Dropbox's content hash algorithm. Dropbox hashes each 4 MiB block with SHA-256, concatenates those block digests, and SHA-256 hashes the concatenation to produce the final checksum.

## Important APIs, types, and functions
- Constants expose `BlockSize`, `Size`, and the internal `bytesPerBlock` of 4 MiB.
- `digest` implements `hash.Hash` with a current block hash, total hash, byte count within the current block, and guards around `Sum` usage.
- `New` returns a reset `hash.Hash` implementation.
- `Write` feeds arbitrary input across 4 MiB block boundaries and writes each completed block digest into the total hash.
- `writeBlockHash` appends the current block digest to `totalHash` and resets block state.
- `Sum` finalizes any partial block into the total hash and returns the total hash digest.
- `Reset`, `Size`, and `BlockSize` satisfy `hash.Hash`.
- Package-level `Sum` computes a checksum for a byte slice and returns a fixed-size array.

## Control flow
Callers create a digest with `New`, stream data through `Write`, then call `Sum`. `Write` slices the input into whatever fits before the next 4 MiB boundary, updates the block hash, and flushes the block digest whenever the block reaches 4 MiB. `Sum` flushes a non-empty final partial block and then returns the SHA-256 digest of all block digests. Empty input returns the SHA-256 of empty data because no block digest is written.

## State and persistence behavior
All state is in memory. `digest.n` tracks current block fill, `blockHash` tracks the current block, `totalHash` tracks the concatenated block digests, and `sumCalled`/`writtenMore` protect against unsupported `Sum`, then `Write`, then `Sum` reuse. `Reset` clears all state.

## Dependencies and integration points
The implementation only depends on the Go standard library `crypto/sha256` and `hash` interfaces. The Dropbox backend can use it wherever Dropbox content hashes are needed for verification or metadata comparison.

## Risks and edge cases
- `Sum` mutates internal state by flushing a partial block, despite the `hash.Hash` contract saying `Sum` should not change state. The code documents that calling `Sum`, then `Write`, then `Sum` panics.
- The exported `Size` constant is set to `sha256.BlockSize` rather than `sha256.Size`, so package-level `Sum` returns a 64-byte array with only the first 32 bytes populated by the digest. The `hash.Hash.Size()` method still reports 32 via `totalHash.Size()`. This API shape is covered by tests and may be relied upon.
- Panics occur if underlying hash writes unexpectedly return errors, which standard SHA-256 should not do.
- Boundary correctness at exactly 4 MiB and multiples is essential to match Dropbox.

## Test signals
`dbhash_test.go` validates known Dropbox content hashes across many lengths around 4 MiB and 8 MiB boundaries and across many caller chunk sizes. It also tests the documented `Sum` reuse panic, `Size`, `BlockSize`, and package-level `Sum` behavior.
