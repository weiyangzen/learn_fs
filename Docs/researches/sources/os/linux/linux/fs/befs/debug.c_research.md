# File Research: sources/os/linux/linux/fs/befs/debug.c

## Purpose
Provides BeFS logging and optional debug dump helpers.

## Main Functions
- `befs_error()`: emits `pr_err` with superblock ID prefix.
- `befs_warning()`: emits `pr_warn` with superblock ID prefix.
- `befs_debug()`: emits `pr_debug` only under `CONFIG_BEFS_DEBUG`.
- `befs_dump_inode()`: debug-dumps raw inode fields, block runs, timestamps, symlink or datastream layout.
- `befs_dump_super_block()`: debug-dumps raw superblock fields.
- `befs_dump_index_entry()`: debug-dumps B+tree superblock fields.
- `befs_dump_index_node()`: debug-dumps B+tree node header fields.

## Conditional Code
Most dump output is compiled behind `CONFIG_BEFS_DEBUG`. There is also an unused `#if 0` block for small-data and run dumping.

## Dependencies
Uses endian conversion helpers and BeFS structures through `befs.h`.

## Research Notes
The file intentionally keeps runtime overhead low unless debug is enabled. Error and warning paths remain active and include the filesystem identifier.
