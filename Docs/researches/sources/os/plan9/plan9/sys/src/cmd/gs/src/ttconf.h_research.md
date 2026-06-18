# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconf.h

Purpose: Ghostscript-adapted configuration header for the TrueType interpreter.

Key contents:
- Undefines autoconf-style feature macros not used here.
- Defines `WORDS_BIGENDIAN` from `ARCH_IS_BIG_ENDIAN`.
- Defines `HAVE_MEMCPY`.
- Defines `SIZEOF_INT` and `SIZEOF_LONG` from Ghostscript `ARCH_LOG2_SIZEOF_*`.
- Leaves other platform features such as `mmap`, `valloc`, `fcntl.h`, `unistd.h`, and `basename` disabled.

Dependencies: architecture macros from Ghostscript standard headers.

Integration notes: included by `ttconfig.h` to feed FreeType-derived compile-time decisions.

Risks: intentionally static configuration may need adjustment if ported outside Ghostscript’s architecture setup.
