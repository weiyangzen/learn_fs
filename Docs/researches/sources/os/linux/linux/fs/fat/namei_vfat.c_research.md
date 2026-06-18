# File Research: sources/os/linux/linux/fs/fat/namei_vfat.c

## Purpose
Implements the `vfat` namespace layer: long filename handling, short alias generation, case-sensitive/case-insensitive dentry behavior, lookup/create/delete/mkdir/rename including `RENAME_EXCHANGE`, and filesystem registration.

## Main Responsibilities
- Provides dentry hash/compare/revalidate logic for VFAT names.
- Converts user names to UTF-16 long-name slots.
- Generates unique 8.3 aliases for long names.
- Builds long-name slot chains plus short entries.
- Implements VFAT create, lookup, unlink, rmdir, mkdir, rename, and exchange.
- Registers the `vfat` filesystem type.

## Key Interfaces
- `vfat_hash()` / `vfat_hashi()`, `vfat_cmp()` / `vfat_cmpi()`: case-sensitive or case-insensitive dentry operations.
- `vfat_revalidate()` / `vfat_revalidate_ci()`: validates negative dentries using parent i_version.
- `vfat_create_shortname()`: creates unique 8.3 aliases and lower-case flags.
- `xlate_to_uni()`: converts input names to UTF-16, including `uni_xlate` escape decoding.
- `vfat_build_slots()`: builds long-name slots and final short entry.
- `vfat_add_entry()` / `vfat_find()`: shared add/search helpers.
- `vfat_lookup()`, `vfat_create()`, `vfat_mkdir()`, `vfat_unlink()`, `vfat_rmdir()`: namespace operations.
- `vfat_rename2()`: dispatches normal rename or exchange rename.

## Important Behavior
VFAT strips trailing dots from lookup/hash names. In case-insensitive mode, negative dentries are dropped for create/rename target intents so a newly specified case can be used. Negative dentries store the parent inode version to detect short-alias creation invalidating a previous negative lookup.

`vfat_create_shortname()` decides whether a name can be represented as a valid short name, whether a long-name slot is still required for case or multibyte preservation, and whether numeric tails are needed. It tries `~1` through `~9`, then uses jiffies-derived hexadecimal tails.

`vfat_build_slots()` converts to UTF-16, rejects bad characters/trailing space, creates an alias, emits long-name slots in reverse order with checksum when needed, then creates the short entry with VFAT creation/access/modify timestamps.

Rename detaches and reattaches inode `i_pos` mappings. Cross-directory directory renames update `..` and parent link counts. `RENAME_EXCHANGE` swaps two inode positions and updates both `..` entries when needed, with rollback attempts and corruption reporting on failures.

## Dependencies
Uses shared FAT directory entry allocation/search/removal, inode attach/detach/build/sync, timestamp helpers, NLS tables from mount setup, and dentry/VFS APIs.

## Research Notes
This file is where VFAT compatibility policy is most visible: trailing-dot semantics, casefold behavior, long-name checksum linkage, numeric-tail aliasing, and negative-dentry invalidation all protect the dual-name model of long names plus 8.3 aliases.
