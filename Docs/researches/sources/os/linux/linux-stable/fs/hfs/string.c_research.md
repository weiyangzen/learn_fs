# File Research: sources/os/linux/linux-stable/fs/hfs/string.c

## Scope

Implements classic HFS case-insensitive Macintosh filename hashing, ordering, and dentry comparison.

## APIs And Behavior

- `caseorder[256]` defines HFS case-folded lexical ordering for Macintosh character bytes.
- `hfs_hash_dentry()` hashes up to `HFS_NAMELEN` bytes using `caseorder`.
- `hfs_strcmp()` compares two byte strings by HFS lexical order, falling back to length difference.
- `hfs_compare_dentry()` checks dentry-name equality under the same case-folded ordering and HFS name-length truncation rules.

## State And Dependencies

Exports are visible to KUnit through `EXPORT_SYMBOL_IF_KUNIT`. The functions are used by catalog key comparison and dentry operations.

## Risks And Invariants

The comparison is byte-table based, not Unicode normalization. Names at or above `HFS_NAMELEN` are truncated for hashing/comparison in ways that must match catalog key construction and VFS dentry behavior.
