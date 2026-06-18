# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stat.h

## Role

Defines `stat`/`stat64` ABI structures, mode bits, file-type predicates, timestamp aliases, large-file symbol mapping, 32-bit syscall views, and file mode-related function prototypes.

## Key Contents

Selects namespace-safe time definitions depending on standards mode. Defines kernel and user variants of `struct stat` and `struct stat64` for LP64 and ILP32. Handles `_FILE_OFFSET_BITS=64` remapping and LP64 large-file aliases through pragma or macro redirection.

Defines 32-bit kernel views `stat32` and `stat64_32`, including packing for alignment differences. Provides file type bits, permission bits, special bits, POSIX permission macros, `S_IS*` predicates, POSIX.4 type macros, x86 SVR4 version constants, and `UTIME_NOW`/`UTIME_OMIT`.

## Interfaces

Declares `chmod`, `fchmod`, `mkdir`, `mkfifo`, `umask`, large-file `stat64` family, and `*at`/timestamp functions when enabled. Includes `<sys/stat_impl.h>` for additional non-kernel declarations.

## Design Notes

This header is dominated by ABI preservation across standards modes, LP64/ILP32, large-file transition, and old x86 compatibility.
