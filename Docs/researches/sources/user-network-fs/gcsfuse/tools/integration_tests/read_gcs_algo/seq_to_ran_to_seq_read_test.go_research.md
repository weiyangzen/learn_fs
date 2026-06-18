# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_to_ran_to_seq_read_test.go

## Purpose

This test exercises a read pattern that begins with reads currently classified as sequential, shifts into random backward reads, then performs a large read expected to re-enter sequential behavior under the existing read algorithm.

## Important APIs, Types, and Functions

`TestSeqReadThenRandomThenSeqRead` creates a 50 MiB test file and calls `operations.ReadAndCompare` at offsets 40 MiB, 35 MiB, 30 MiB, 25 MiB, 20 MiB, and finally 10 MiB with a 40 MiB read size.

## Control Flow

The test intentionally reads backward in 1 MiB chunks. A comment documents that the current algorithm treats the first two reads as sequential. After several random reads, it performs a larger 40 MiB read from 10 MiB, which should be converted to sequential by current logic. Every step validates mounted content against the local disk source.

## State and Persistence Behavior

The mounted file and local disk file persist for the duration of the test. The sequence is stateful with respect to GCSFuse's per-handle or per-reader algorithm heuristics; changing the ordering changes the behavior under test.

## Dependencies and Integration Points

The test uses `operations.CreateFileAndCopyToMntDir`, `operations.ReadAndCompare`, `OneMB`, and `DirForReadAlgoTests`. It is coupled to the read algorithm behavior documented in an inline GitHub URL for an older implementation.

## Risks and Edge Cases

The test checks correctness but not structured evidence that the algorithm actually classified reads as sequential or random. If the algorithm changes but still returns correct bytes, this test may continue passing. Conversely, if future behavior intentionally changes classification, the comments may become stale without affecting assertions.

## Test Signals

The primary signal is byte-for-byte equality through an access pattern that crosses sequential/random/sequential heuristics. Failures indicate stateful reader transition bugs, range handling errors, or large-read fallback problems.
