# File Research: sources/os/linux/linux/fs/befs/super.h

## Purpose
Prototype header for BeFS superblock load and validation.

## Interfaces
- `befs_load_sb()`: copy/convert on-disk superblock into in-memory private state.
- `befs_check_sb()`: validate private superblock state.

## Research Notes
Used by `linuxvfs.c` during mount.
