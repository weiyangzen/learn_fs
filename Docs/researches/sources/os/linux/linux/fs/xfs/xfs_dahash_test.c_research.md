# File Research: sources/os/linux/linux/fs/xfs/xfs_dahash_test.c

Provides an init-time regression test for XFS directory/attribute name hashing.

Key contents:
- A 4096-byte aligned pseudo-random test buffer.
- A table of 100 test cases, each with a start offset, length, expected normal directory/attribute hash, and expected ASCII case-insensitive hash.
- `xfs_dahash_test` iterates the test cases, computing `xfs_da_hashname` and `xfs_ascii_ci_hashname`, counting mismatches.
- On any mismatch, it prints a kernel error and returns `-ERANGE`; otherwise it returns success.

This file protects the on-disk hash algorithm from accidental changes, which matters because directory and attribute btree ordering depends on stable hash values.
