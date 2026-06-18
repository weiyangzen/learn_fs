# File Research: sources/os/linux/linux/fs/hpfs/name.c

Purpose: Implements HPFS filename validation, case conversion, comparison, long-name detection, and OS/2 trailing character normalization.

Key functions:
- `hpfs_chk_name()` rejects names longer than 254 bytes, empty names after adjustment, `.`/`..`, and forbidden characters.
- `hpfs_translate_name()` optionally lowercases names for presentation using the mounted codepage table.
- `hpfs_compare_names()` compares names case-insensitively with HPFS ordering and sentinel handling.
- `hpfs_is_name_long()` applies DOS 8.3-style heuristics to set the HPFS long-name flag.
- `hpfs_adjust_length()` trims trailing dots and spaces except for `.` and `..`.

Dependencies and integration:
- Used by dcache operations, lookup, readdir, dnode insertion/search, and namespace mutation.

Risk notes:
- Name equivalence includes case folding and trailing-dot/space trimming, so VFS behavior must stay aligned with dentry hashing/comparison.
