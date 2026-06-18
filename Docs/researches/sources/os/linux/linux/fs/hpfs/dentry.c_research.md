# File Research: sources/os/linux/linux/fs/hpfs/dentry.c

Purpose: Implements HPFS dcache hashing and comparison using HPFS filename normalization and case folding.

Key functions:
- `hpfs_hash_dentry()` trims OS/2-style trailing dots/spaces except for `.`/`..`, uppercases through HPFS codepage rules, and computes the dentry hash.
- `hpfs_compare_dentry()` validates the candidate name, adjusts existing-name length, and compares case-insensitively with HPFS ordering rules.

Dependencies and integration:
- Uses name helpers from `name.c` and codepage table stored in `hpfs_sb_info`.
- Exports `hpfs_dentry_operations`.

Risk notes:
- Dcache behavior intentionally mirrors HPFS name equivalence, including trailing-dot/space trimming.
