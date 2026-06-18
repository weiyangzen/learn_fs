# sources/object-store/minio/cmd/erasure-decode_test.go

Purpose: Validates `Erasure.Decode` correctness and performance across erasure layouts, bitrot algorithms, offline/faulty disks, and ranged reads.

Important APIs/types/functions: Extends `badDisk` with `ReadFile` failure behavior. `erasureDecodeTests` enumerates data-block counts, total disks, offline disks, block sizes, object sizes, offsets, lengths, algorithms, and expected failure/quorum behavior. `TestErasureDecode` writes random data through `Erasure.Encode`, constructs bitrot readers, decodes ranges, compares bytes, then injects bad/nil readers to verify quorum behavior. `TestErasureDecodeRandomOffsetLength` stress-tests random ranges when not in short mode. Benchmarks exercise common data/parity layouts and failure mixes.

Control flow and state: Each case creates a temporary erasure setup, encodes random data, reopens shard readers with expected checksums, decodes into a buffer, and cleans up readers/writers. Fault injection replaces reader disks with `badDisk` or nil entries.

Dependencies and integration points: Depends on test setup helpers, bitrot readers/writers, `DefaultBitrotAlgorithm`, `BLAKE2b512`, `SHA256`, and `Erasure.Encode` as the writer-side counterpart. It tests decode as part of the storage stack rather than isolated Reed-Solomon calls.

Risks: Random data improves coverage but limits exact reproducibility of failing byte patterns. The long random-offset test is skipped under short mode and can be expensive. Some benchmark logic mutates writer state to simulate down disks.

Test signals: Strong coverage for boundary offsets, quorum thresholds, bitrot reader failures, and byte-for-byte range reconstruction.
