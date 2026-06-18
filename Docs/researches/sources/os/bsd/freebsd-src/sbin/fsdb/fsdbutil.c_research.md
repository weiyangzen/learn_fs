# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdbutil.c

## Purpose

Helper routines for `fsdb` command parsing and inode display/validation.

## Main Functions

- `crack()`: tokenizes a command line into up to 8 whitespace-separated arguments.
- `recrack()`: tokenizes with a maximum argument count, preserving the remaining text as the final argument.
- `argcount()`: prints command argument-count errors and usage.
- `printstat()`: prints inode type, mode, size, times, owner/group, link count, flags, block count, and generation.
- `checkactive()`: verifies that a current inode is loaded.
- `checkactivedir()`: verifies that current inode is a directory.
- `printactive()`: prints current inode stats or block list.

## Integration Points

Calls `prtblknos()` for block display and uses `sblock`, `DIP()`, UFS1/UFS2 timestamp handling, passwd/group lookup, and current inode globals from `fsdb.h`.

## Risk Notes

`recrack()` assumes at least one parsed token before it computes `argv[i - 1]`, matching its intended use for already validated command lines with a final free-form argument.
