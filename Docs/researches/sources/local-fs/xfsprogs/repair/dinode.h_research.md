# File Research: sources/local-fs/xfsprogs/repair/dinode.h

## Role

`dinode.h` declares the inode and bmbt processing API used across xfs_repair phases.

## Exposed API

- `convert_extent`: converts a disk bmbt record into offset, start block, block count, and flags.
- `process_bmbt_reclist`: validates a bmbt record list and updates block accounting.
- `scan_bmbt_reclist`: validates a record list against duplicate extents without updating global ownership.
- `process_dinode`: full inode verification/repair entrypoint.
- `verify_dinode`: core validation for known inodes.
- `verify_uncertain_dinode`: quiet validation for candidate inodes.
- `process_uncertain_aginodes`, `process_aginodes`, `check_uncertain_aginodes`: AG-level inode scan workflow hooks.
- `get_agino_buf`: random-access inode cluster read helper.
- `dinode_bmbt_translation_init`, `get_forkname`: translation/string helpers for diagnostics.

## Interactions

This header binds phase drivers, directory repair, bmap scanning, and inode discovery to `dinode.c`. It intentionally exposes only high-level inode processing functions and keeps the detailed repair policy private to `dinode.c`.
