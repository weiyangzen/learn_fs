# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/error.c

Defines global Vac error string variables.

Errors include:
- Missing/unallocated directory entry.
- No such file/path and bad path.
- Corrupted directory or metadata.
- Not directory/file.
- I/O error.
- Bad offset, too big, read-only, removed.
- Illegal block address.
- Directory not empty, file exists, cannot remove root.

These strings are declared in `error.h` and used across the Vac implementation for `werrstr`-style reporting.
