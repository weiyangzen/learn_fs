# File Research: sources/os/linux/linux-stable/fs/hfs/string_test.c

## Scope

KUnit tests for classic HFS string comparison, hashing, and dentry comparison.

## Tests Covered

- `hfs_strcmp_test()` checks equal/unequal strings, length ordering, case-insensitive equality, special-character differences, and one-byte boundaries.
- `hfs_hash_dentry_test()` checks successful hashing and verifies case-insensitive names hash equally.
- `hfs_compare_dentry_test()` checks exact/case-insensitive equality, length mismatches, empty strings, and an `HFS_NAMELEN` boundary case.

## Dependencies And Risks

The tests import the KUnit-exported string helpers and use minimal dummy dentries. The coverage is useful for basic behavior but does not validate the full Macintosh `caseorder` table, non-ASCII Mac encodings, or catalog ordering edge cases.
