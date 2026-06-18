# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_diff_block_size_test.go

## Purpose

This test checks sequential reads with block sizes below, equal to, non-multiple of, and multiple of the typical 1 MiB kernel buffer size. It targets range assembly and sequential-read detection around varied read sizes.

## Important APIs, Types, and Functions

`testCase` stores a subtest name, offset, and chunk size. `TestReadSequentialWithDifferentBlockSizes` creates a 10 MiB local/mounted file pair and runs `operations.ReadAndCompare` for chunk sizes 0.5 MiB, 1 MiB, 1.5 MiB, and 5 MiB.

## Control Flow

The test builds a static table of read sizes at offset zero, then runs a subtest for each case. Each subtest reads the mounted file and local disk file at the same offset and compares bytes through the shared operations helper.

## State and Persistence Behavior

The only persisted state is the generated test file in local disk and in the mounted bucket directory. The subtests share the same file pair, so earlier reads may warm caches or read-ahead state for later subtests depending on mount configuration.

## Dependencies and Integration Points

It depends on `OneMB` and `DirForReadAlgoTests` from the package harness and on `operations.CreateFileAndCopyToMntDir` and `operations.ReadAndCompare`. It runs under the harness-provided GCSFuse flags.

## Risks and Edge Cases

Because subtests share one file and always start at offset zero, caching/read-ahead warmed by earlier subtests can influence later cases. The test validates correctness, not exact algorithm classification or number of backend requests. It will not catch performance-only regressions unless they cause incorrect data or errors.

## Test Signals

Passing subtests show that reads of common and irregular block sizes return byte-identical data to local disk. Failures suggest short-read handling, range boundary, or buffer aggregation problems.
