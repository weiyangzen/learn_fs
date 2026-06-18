# File Research: sources/os/bsd/dragonflybsd/sys/sys/unistd.h

## Summary
Kernel-shared POSIX/BSD option, access, seek, pathconf, rfork, and extended-exit constants.

## Main Responsibilities
- Defines POSIX feature-option values and `_POSIX_VERSION`.
- Defines access-mode constants and seek whence values, including BSD `SEEK_DATA` and `SEEK_HOLE`.
- Defines `_PC_*` pathconf names for POSIX, BSD ACL/capability options, and minimum hole size.
- Defines BSD `rfork()` flags and extended-exit bit encoding.

## Important Behavior
The comments distinguish unsupported features (`-1`), conditionally discoverable features (`0`), and implemented versioned features. Saved IDs are deliberately not advertised despite partial implementation notes.

## Risks
These constants are ABI-visible and must stay aligned with libc, syscall implementations, `<fcntl.h>`, and `<stdio.h>`.
