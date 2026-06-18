# File Research: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.c

This file defines lookup tables for rendering byte values as printable strings. It backs the `unctrl()` and `unctrllen()` macros declared in `unctrl.h`.

Key data:
- `__unctrl[256]` maps bytes to display strings:
  - ASCII control bytes become caret notation such as `^A`.
  - Printable ASCII maps to one-character strings.
  - DEL maps to `^?`.
  - High bytes map to lowercase hex strings like `0x80`.
- `__unctrllen[256]` stores the corresponding display lengths.
- Under `HAVE_WCHAR`, `__wunctrl[256]` provides wide-string equivalents.

Integration:
- Used by curses tracing and callers that need display-safe representations of control characters.
- Exported through macros rather than functions in `unctrl.h`.

Risks and notes:
- The tables are static mappings for 8-bit byte values, not locale-sensitive Unicode display conversion.
- High-byte values are rendered as hex byte strings rather than decoded multibyte characters.
