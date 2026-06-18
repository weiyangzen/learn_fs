# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.c

## Purpose
Provides an init-time deterministic regression test for XFS directory/attribute name hash functions.

## Main Data
Contains a 4096-byte aligned random test buffer and 100 test cases. Each test specifies a start offset, length, expected `xfs_da_hashname` result, and expected ASCII case-insensitive hash result.

## Main API
`xfs_dahash_test` iterates all test cases, computes the normal DA hash and `xfs_ascii_ci_hashname`, counts mismatches, prints a kernel error if any mismatch occurs, and returns `-ERANGE` on failure or zero on success.

## Dependencies
Uses directory/attribute hash APIs from XFS dir2/DA code and is marked `__init`/`__initdata`, so the data and function are init-only.
