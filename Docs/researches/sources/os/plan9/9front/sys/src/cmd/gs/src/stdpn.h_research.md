# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpn.h

Deprecated pre-ANSI prototype macro header.

Key points:
- Defines `P0()` through `P16(...)`.
- Comments explain these formerly supported traditional C compilers by hiding argument lists.
- Current definitions preserve typed parameter lists because pre-ANSI compilers are no longer supported.
- Marked deprecated and not intended for new code.

Dependencies and interactions:
- Included by `stdpre.h` for legacy source compatibility.

Research relevance:
- Small historical compatibility layer that keeps older Ghostscript declarations buildable.
