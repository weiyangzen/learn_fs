
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash.go

## Purpose
This package implements HiDrive's hierarchical content hash. It combines SHA-1 block hashes into position-embedded level hashes, supports streaming writes, and exposes binary marshal/unmarshal so hash state can be persisted or copied mid-stream.

## Important APIs, Types, And Control Flow
Constants define a 4096-byte level-0 block, 20-byte output size, and 256 sums per higher level. `writeByBlock` feeds a writer in exact block units while tracking bytes and all-zero blocks. `level` aggregates up to 256 SHA-1-sized sums; for non-null blocks it appends the block position byte before adding the SHA-1 sum into a big-endian checksum with carry. `hidriveHash.Write` hashes 4096-byte data blocks, maps all-zero blocks to `zeroSum`, and propagates full levels upward via `aggregateToLevel`. `Sum` snapshots state, pads a partial block with zeroes, folds incomplete levels, returns the final checksum, and restores state. Both `level` and `hidriveHash` implement binary marshaling.

## State And Persistence
Hash state includes level checksums, counts, partial block/hash bytes, all-null flags, and the last sum written. Binary marshaling serializes this state plus the underlying SHA-1 marshaled state. No external persistence is performed by the package itself.

## Dependencies And Integration Points
It depends on Go `crypto/sha1`, `hash`, `encoding.BinaryMarshaler`, and the internal `LevelHash` interface. `hidrive.go` registers `hidrivehash.New` as rclone's `HiDriveHash`.

## Risks And Test Signals
`level.Write` intentionally violates usual `hash.Hash` expectations by returning `ErrorHashFull` when full; `hidriveHash.aggregateToLevel` panics if a level write errors unexpectedly. `UnmarshalBinary` trusts encoded length fields enough to slice into `b`, so malformed lengths beyond short header cases can panic. Correctness depends on all-zero block handling and padding partial blocks on `Sum`. Tests should use official HiDrive vectors, mixed null ranges, arbitrary write chunk sizes, marshal/unmarshal continuation, reset, and invalid encodings.
