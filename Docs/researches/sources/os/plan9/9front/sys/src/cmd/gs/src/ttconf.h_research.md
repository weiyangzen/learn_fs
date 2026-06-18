# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconf.h

Configuration header for Ghostscript’s TrueType interpreter.

Key points:
- Modified from FreeType configuration.
- Defines `WORDS_BIGENDIAN` from `ARCH_IS_BIG_ENDIAN`.
- Defines `HAVE_MEMCPY`.
- Leaves many platform features undefined: `mmap`, ANSI headers, `getpagesize`, `valloc`, `fcntl.h`, `unistd.h`, `getopt.h`, `conio.h`, and `basename`.
- Defines `SIZEOF_INT` and `SIZEOF_LONG` from Ghostscript `ARCH_LOG2_SIZEOF_*`.

Dependencies and interactions:
- Included by `ttconfig.h`.
- Ties FreeType-derived code to Ghostscript’s generated architecture configuration.

Research relevance:
- Build-configuration adapter between Ghostscript portability macros and imported FreeType code.
