# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unistd_.h

Portable wrapper/substitute for Unix `unistd.h`.

Key points:
- Includes `std.h` before any headers that may include `sys/types.h`.
- Includes `<io.h>` for OS/2 and Win32.
- For MSVC, maps POSIX-like names to CRT underscore forms: `fsync`, `read`, `isatty`, `setmode`, `fstat`, `dup`, `open`, and `close`.
- For Borland Win32, maps a smaller set of functions to underscore forms.
- Falls back to including system `<unistd.h>` elsewhere.

Dependencies and interactions:
- Used by portable Ghostscript modules that need POSIX file-descriptor routines.
- Interacts with Windows compiler wrappers and the broader `std*.h` portability layer.

Research relevance:
- Captures Ghostscript’s old cross-platform file-descriptor compatibility strategy, especially for Windows compilers.
