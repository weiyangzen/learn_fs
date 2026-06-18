# File Research: sources/os/linux/linux-stable/fs/ntfs/collate.h

Purpose: Header for NTFS collation support.

Key contents:
- `ntfs_is_collation_rule_supported()` validates supported collation constants and accepted numeric ranges.
- Declares `ntfs_collate()`.

Supported rules:
- `COLLATION_BINARY`
- `COLLATION_NTOFS_ULONG`
- `COLLATION_FILE_NAME`
- `COLLATION_NTOFS_ULONGS`

Role:
- Used by index parsing/search code to reject unsupported on-disk collation modes before comparing keys.
