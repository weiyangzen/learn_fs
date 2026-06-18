# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/errno_.h

Portable wrapper for `errno.h`.

Key points:
- Includes Ghostscript `std.h` before system headers.
- Includes `<errno.h>`.
- Declares `extern int errno` if `errno` is not already a macro.

Dependencies and interactions:
- Provides a compatibility layer for old or nonconforming C libraries where `<errno.h>` defines error numbers but not the `errno` object.

OS/filesystem relevance:
- Supports portable reporting of OS/file errors across Ghostscript code.
