# sources/sync-backup/syncthing/lib/scanner/blocks.go

## Purpose
Computes Syncthing block-level SHA-256 hashes for file contents and validates block hashes.

## Important APIs, Types, and Functions
`SHA256OfNothing` is the hash for an empty byte slice. `Counter` reports bytes processed. `Blocks` returns `[]protocol.BlockInfo` for an `io.Reader`. `Validate` checks a buffer against a hash. Internal pools `bufPool` and `hashPool` reuse 32 KiB buffers and SHA-256 hash instances.

## Control Flow
`Blocks` optionally wraps the reader in `io.LimitReader` when `sizehint >= 0`, preallocates block and hash storage, then repeatedly copies up to `blocksize` bytes into the hash using a pooled buffer. For each non-empty chunk it updates the counter, appends the SHA-256 digest into a contiguous hash backing slice, creates a `BlockInfo` with size, offset, and hash slice, and resets the hash. Empty input returns one zero-size block with `SHA256OfNothing`. Context cancellation is checked between blocks.

## State and Persistence Behavior
State is temporary pooled buffers/hashers and returned in-memory `BlockInfo` slices. No persistence occurs. Returned hash slices may share a contiguous backing allocation for efficiency.

## Dependencies and Integration Points
Depends on `crypto/sha256`, `io`, `sync`, and `protocol.BlockInfo`. Used by `HashFile`, request validation, and scanner output generation. `Validate` is used to confirm received block contents match advertised hashes.

## Risks and Edge Cases
A non-positive `blocksize` would break `io.LimitReader` semantics, so callers must use protocol block-size helpers. If `sizehint` is wrong and smaller than actual content, the reader is intentionally limited; `HashFile` prevents stale results by checking file size after hashing. Hash backing-slice aliasing is efficient but callers must treat hashes as immutable.

## Test Signals
`blocks_test.go` covers empty input, single-block inputs, multiple block sizes, offsets, sizes, and expected SHA-256 values. `BenchmarkValidate` measures hash validation speed.
