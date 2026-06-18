# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unistd_.h

Portable wrapper/substitute for Unix `unistd.h`.

Key points:
- Includes `std.h` before system headers.
- Includes `<io.h>` for OS/2 and Win32.
- For Microsoft C, maps POSIX-like names to underscore-prefixed CRT calls: `fsync`, `read`, `isatty`, `setmode`, `fstat`, `dup`, `open`, and `close`.
- For Borland C on Win32, maps `fsync`, `read`, `isatty`, and `setmode`.
- Falls back to including system `<unistd.h>` otherwise.

Dependencies and interactions:
- Used by platform I/O code such as `gp_stdia.c` and Windows console make rules.
- Works with Ghostscript’s wrapper-header convention using `_` suffix names.

Research relevance:
- Small but central portability adapter for low-level file descriptor APIs across Unix and Windows compilers.
