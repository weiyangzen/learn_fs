# File Research: sources/local-fs/xfsprogs/db/freesp.h

## Purpose
Declares the free-space reporting command initializer.

## Interfaces
- `freesp_init()` registers the `freesp` command with the xfs_db command table.

## Dependencies
Included by `freesp.c` and by command initialization code that wires xfs_db commands together.
