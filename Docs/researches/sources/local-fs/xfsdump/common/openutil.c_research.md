# File Research: sources/local-fs/xfsdump/common/openutil.c

## Role

This file provides small helpers for constructing paths and opening or creating temporary/housekeeping files.

## Path Construction

`open_pathalloc()` allocates a pathname from directory, basename, and optional PID suffix. It special-cases `/` so generated paths do not contain a double slash.

PID suffixes use `.<pid>`, with room for a 64-bit PID representation.

## File Helpers

- `open_trwp()` creates/truncates a read-write file with user read/write permissions.
- `open_erwp()` creates a read-write file exclusively.
- `open_rwp()` opens an existing file read-write.
- `mkdir_tp()` creates a user-only directory.

The create helpers log failures through `mlog()`.

## Directory/Basename Helpers

`open_trwdb()`, `open_erwdb()`, and `open_rwdb()` combine path allocation with the corresponding pathname-based open helper and free the temporary path buffer.
