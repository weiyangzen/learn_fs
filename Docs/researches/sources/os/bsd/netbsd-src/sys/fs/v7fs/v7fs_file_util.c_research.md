# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file_util.c

## Purpose
Provides higher-level file utilities for hard links, symbolic links, rename, directory-entry replacement, lookup by inode number, and directory-move validation.

## Main Interfaces
- `v7fs_file_link()` adds a directory entry and increments the target inode link count.
- `v7fs_file_symlink()` stores the symlink target in a single allocated data block.
- `v7fs_file_rename()` handles replacement of existing targets, adds the destination entry, removes the source entry, and updates `..` when moving directories between parents.
- `v7fs_directory_replace_entry()` changes an existing dirent inode number.
- `v7fs_file_lookup_by_number()` finds a name for an inode in a parent directory.

## Implementation Notes
`can_dirmove()` walks destination parents via `..` to prevent moving a directory into its own descendant. Symlink targets are limited to the V7/2BSD maximum and include a trailing NUL.

## Dependencies
Uses `v7fs_datablock_foreach()`, dirent conversion, core directory add/remove, inode load/writeback, and scratch I/O.
