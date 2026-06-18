# File Research: sources/os/linux/linux-stable/fs/hpfs/name.c

## Purpose

Implements HPFS filename validation, case mapping, comparison, lowercase presentation, long-name detection, and OS/2 trailing-dot/space trimming.

## Main Entry Points

- `hpfs_upcase()`
- `hpfs_chk_name()`
- `hpfs_translate_name()`
- `hpfs_compare_names()`
- `hpfs_is_name_long()`
- `hpfs_adjust_length()`

## Control Flow And State

Validation rejects names longer than 254 bytes, empty names after trimming, reserved characters, `.`, and `..`. Comparison uppercases through the mount code-page table and treats HPFS last sentinel entries as greater than all real names. Lowercase translation allocates a new name buffer only when the lowercase mount option is active.

## Dependencies

Uses the per-superblock code-page table loaded from disk.

## Risks

Name collation must match HPFS directory-tree ordering. `hpfs_is_name_long()` appears to test `name[i]` instead of `name[j]` in the extension loop, preserving existing kernel behavior but making the long-name flag check subtle.
