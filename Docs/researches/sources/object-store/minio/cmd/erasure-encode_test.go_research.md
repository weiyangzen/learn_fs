# sources/object-store/minio/cmd/erasure-encode_test.go

Purpose: Tests erasure encode behavior across layouts, data sizes, offsets, algorithms, and disk-failure/quorum scenarios, and provides encode benchmarks.

Important APIs/types/functions: Defines `badDisk` with failing write/read/create methods and `Hostname`. `erasureEncodeTests` includes many combinations of data/parity counts, total disks, offline disks, block size, object size, source offset, bitrot algorithm, and expected quorum failure. `TestErasureEncode` creates erasure setups, writes random data through bitrot writers, validates byte counts, then injects nil/bad writers to assert quorum outcomes. Benchmarks measure write throughput under selected down-disk patterns.

Control flow and state: The test first verifies a normal encode for each case, updates disk state for failed writers, then repeats with injected failures. Temporary disk state is owned by the test setup and removed by helpers.

Dependencies and integration points: Exercises `Erasure.Encode`, `newBitrotWriter`, writer close/checksum behavior, and storage test fixtures. It is also the source of the shared `badDisk` type used by decode/heal tests.

Risks: Test cases rely on the exact `quorum := dataBlocks+1` used in production-like writes. The injected failure count and writer nil placement are important for matching expected quorum outcomes.

Test signals: Strong write-path regression coverage, including empty data and high data-block counts.
