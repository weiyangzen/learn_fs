# File Research: sources/os/linux/linux-stable/fs/hpfs/dentry.c

## Purpose

Defines HPFS dcache hashing and comparison behavior for case-insensitive, OS/2-style filename rules.

## Main Entry Points

- `hpfs_hash_dentry()`
- `hpfs_compare_dentry()`
- `hpfs_dentry_operations`

## Control Flow And State

Hashing trims trailing dots/spaces except for `.` and `..`, then hashes uppercase-normalized bytes using the mounted code-page table. Comparison validates the candidate name and compares names through `hpfs_compare_names()`.

## Dependencies

Depends on name helpers and `sb_cp_table`.

## Risks

Correct dcache behavior depends on matching on-disk HPFS collation and trimming rules. Invalid lookup names fail comparison rather than matching existing dentries.
