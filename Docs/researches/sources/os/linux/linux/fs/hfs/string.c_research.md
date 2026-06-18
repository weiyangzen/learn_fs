# File Research: sources/os/linux/linux/fs/hfs/string.c

Purpose: Implements classic HFS case-insensitive Macintosh filename hashing, ordering, and dentry comparison.

Key functions:
- `hfs_hash_dentry()` hashes names through the ARDI-derived `caseorder` table and truncates to `HFS_NAMELEN`.
- `hfs_strcmp()` compares two byte strings in Macintosh lexical/casefold order.
- `hfs_compare_dentry()` tests dentry name equality under the same casefold order.

Dependencies and integration:
- Used by catalog key comparison and dentry operations in `sysdep.c`.
- Functions are exported for KUnit under `EXPORT_SYMBOL_IF_KUNIT`.

Risk notes:
- The table is byte-oriented Mac Roman behavior, not Unicode normalization.
- `hfs_compare_dentry()` treats long lookup names through `HFS_NAMELEN` truncation semantics.
