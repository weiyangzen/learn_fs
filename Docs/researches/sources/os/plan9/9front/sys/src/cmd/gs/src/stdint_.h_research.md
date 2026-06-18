# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdint_.h

Generic substitute for C99 `stdint.h`.

Key points:
- Includes `std.h`.
- Uses real `<stdint.h>` when `HAVE_STDINT_H` is set, with a MacOS shortcut.
- Accepts stdint-like types from `sys/types.h` when `SYS_TYPES_HAS_STDINT_TYPES` is set.
- Provides platform-specific definitions for Win32/MSVC, OpenVMS, and Cygwin.
- Falls back to `arch.h`-derived typedefs for 8-, 16-, 32-, and 64-bit signed/unsigned integer types.

Dependencies and interactions:
- Used by jbig2dec headers, TrueType bytecode/interpreter code, and other code requiring exact-size integers.
- Relies on `ARCH_SIZEOF_*` from `arch.h`.

Research relevance:
- This protects bundled older code from missing C99 integer headers on legacy or non-Unix platforms.
