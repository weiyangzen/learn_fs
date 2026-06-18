# sources/object-store/minio/cmd/bitrot.go

This file defines MinIO's bitrot algorithm registry, verifier type, factories for whole-file versus streaming bitrot readers/writers, helper close/sum/size routines, stream verification logic, and startup self-test.

The supported algorithms map `SHA256`, `BLAKE2b512`, `HighwayHash256`, and `HighwayHash256S` to string names. `BitrotAlgorithm.New` constructs the corresponding `hash.Hash`, using MinIO's SHA-256 implementation, `blake2b.New512`, or HighwayHash with a fixed 256-bit magic key. `Available`, `String`, `BitrotAlgorithmFromString`, and `NewBitrotVerifier` provide lookup and verification helpers.

`newBitrotWriter` and `newBitrotReader` dispatch to streaming implementations only for `HighwayHash256S`; all other algorithms use whole-file mode. `closeBitrotReaders` and `closeBitrotWriters` close heterogeneous reader/writer slices and preserve per-writer errors. `bitrotWriterSum` returns the whole-file writer checksum and `nil` for streaming writers. `bitrotShardFileSize` accounts for per-shard hash overhead in streaming mode.

`bitrotVerify` verifies either a whole stream against one expected checksum or a streaming layout of repeated hash/data shards. The streaming branch first checks protected file size, uses an ODirect small buffer, reads each stored hash, hashes the following data shard, and returns corruption errors on short reads or mismatches. `bitrotSelfTest` computes deterministic chained hashes for each available algorithm and fatally aborts if any checksum differs from known constants.

Dependencies include highwayhash, BLAKE2b, MinIO SHA-256, internal IO pools, logging, and storage-facing errors. Risks center on algorithm registry compatibility, hard-fail behavior for unsupported algorithms, correct size accounting for streaming layouts, distinguishing `errFileCorrupt` from underlying I/O errors, and self-test constants staying aligned with algorithm implementations. `bitrot_test.go` verifies basic writer/reader interoperability for every registered algorithm.
