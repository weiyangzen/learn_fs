# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdint_.h

Purpose: Ghostscript substitute for C99 `stdint.h`.

Key contents:
- Includes `std.h` first to establish Ghostscript architecture and base typedefs.
- Uses native `<stdint.h>` when `HAVE_STDINT_H` is available, with a MacOS fallback.
- Accepts environments where `sys/types.h` already supplied fixed-width types.
- Provides platform-specific typedefs for Win32, VMS, and Cygwin.
- Falls back to `ARCH_SIZEOF_*` checks for 8-, 16-, 32-, and 64-bit signed/unsigned integer types.

Dependencies: `std.h`, optional `<stdint.h>`/`<inttypes.h>`.

Integration notes: `ttfsfnt.h` includes this header to define TrueType exact-size aliases (`uint8`, `int16`, `uint32`, etc.).

Risks: fallback branches assume exactly matching architecture sizes; if `ARCH_SIZEOF_LONG_LONG` is unavailable on a 32-bit compiler without 64-bit support, `int64_t`/`uint64_t` may not be defined.
