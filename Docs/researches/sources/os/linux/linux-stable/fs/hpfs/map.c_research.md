# File Research: sources/os/linux/linux-stable/fs/hpfs/map.c

## Purpose

Maps HPFS on-disk metadata structures into memory and validates them under configured check levels.

## Main Entry Points

- `hpfs_map_dnode_bitmap()`, `hpfs_map_bitmap()`, `hpfs_prefetch_bitmap()`
- `hpfs_load_code_page()`
- `hpfs_load_bitmap_directory()`
- `hpfs_load_hotfix_map()`
- `hpfs_map_fnode()`, `hpfs_map_anode()`, `hpfs_map_dnode()`
- `hpfs_fnode_dno()`

## Control Flow And State

Bitmap mapping loads four-sector bitmaps through the bitmap directory and prefetches following bitmaps. Code-page loading validates directory/data offsets and builds a 256-byte upper/lowercase table. Hotfix loading validates spare counts and copies remap arrays.

Fnode/anode/dnode mapping wraps buffer helpers and, when checks are enabled, validates magic, self pointers, B+ tree node counts, first-free offsets, EA bounds, and dirent layout.

## Dependencies

Uses buffer mapping helpers, HPFS on-disk structures, allocation-sector checks, and superblock state.

## Risks

Validation is central to avoiding bad pointer arithmetic in higher-level code. In readonly mode, one dnode name-length mismatch is tolerated if the stored dirent is larger than expected. Incorrect check-level behavior can either reject mountable damaged volumes or allow later corruption.
