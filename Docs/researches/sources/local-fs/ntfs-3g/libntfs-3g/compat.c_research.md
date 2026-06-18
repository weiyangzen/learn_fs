# File Research: sources/local-fs/ntfs-3g/libntfs-3g/compat.c

## Role

Provides fallback implementations for libc/platform functions that may be missing on target systems. This supports NTFS-3G portability across Unix-like environments.

## Main Functions

- `ffs()` is compiled when `HAVE_FFS` is absent. It returns the 1-based index of the least significant set bit, or 0 for input 0.
- `daemon()` is compiled when `HAVE_DAEMON` is absent. It forks, exits the parent, calls `setsid()`, optionally changes directory to `/`, and optionally redirects stdin/stdout/stderr to `/dev/null`.
- `strsep()` is compiled when `HAVE_STRSEP` is absent. It tokenizes a mutable string using delimiter characters and supports empty tokens.

## Dependencies

Includes only `compat.h` unconditionally, with conditional system headers for `daemon()` and `strsep()`.

## Important Behavior

The fallback `daemon()` is the classic BSD/OpenSolaris-style implementation and performs a single fork. The fallback `strsep()` modifies the input string in place by writing NUL terminators.

## Research Notes

This file contains compatibility glue only. It has no NTFS metadata logic but affects code such as `dir.c`, which uses `ffs()` for deriving block-size bit shifts when native `ffs()` is unavailable.
