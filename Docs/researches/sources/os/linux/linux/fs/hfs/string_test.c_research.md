# File Research: sources/os/linux/linux/fs/hfs/string_test.c

Purpose: KUnit coverage for HFS filename comparison, hashing, and dentry equality.

Key tests:
- `hfs_strcmp_test()` covers equal strings, unequal strings, length ordering, case-insensitive equality, special characters, and single-character cases.
- `hfs_hash_dentry_test()` verifies hash success, case-insensitive same hashes, and different-name hash differences.
- `hfs_compare_dentry_test()` checks exact, case-insensitive, mismatched, length-mismatched, empty, and name-length-boundary comparisons.

Dependencies and integration:
- Requires KUnit and imports `EXPORTED_FOR_KUNIT_TESTING`.
- Tests exported symbols from `string.c`.

Risk notes:
- These tests assert intended behavior at a high level but do not exhaust the 256-entry Mac case-order table.
