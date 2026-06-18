# File Research: sources/local-fs/xfsprogs/db/input.h

## Purpose
Declares xfs_db input parsing and input-stream stack helpers.

## Interfaces
- `breakline()` converts a mutable command string into argv.
- `doneline()` frees input/argv allocations.
- `fetchline()` returns the next command line.
- `input_init()` registers input-related commands.
- `pushfile()` pushes an input stream.
