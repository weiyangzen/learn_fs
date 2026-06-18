# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixansi.mak

Unix/ANSI C/X11 Ghostscript makefile for non-gcc ANSI compilers.

Key points:
- Mirrors `unix-gcc.mak` structure but leaves `CC` unset for a platform ANSI compiler.
- Uses simpler flags: `CFLAGS_STANDARD=-O`, `CFLAGS_DEBUG=-g`, `CFLAGS_PROFILE=-pg -O`.
- Configures install paths, runtime resource paths, JPEG/libpng/zlib/JBIG2/icclib/ijs sources, X11 settings, `SYNC=nosync`, and `STDLIBS=-lm`.
- Enables the same major language features as Unix gcc: PostScript Level 3, PDF, DPS Next, TrueType fonts, EPSF, pipe, and FAPI.
- Defines a somewhat smaller/default device list than `unix-gcc.mak`, with overflow device variables for PNM-style devices.
- Includes the same core Unix/interpreter/library/device/install make fragments except gcc-specific `cc.tr`.

Dependencies and interactions:
- Intended for hand-edited platform builds where gcc is not the compiler.
- Notes that callers should define a 64-bit `GX_COLOR_INDEX_TYPE` if available.

Research relevance:
- Shows the non-gcc Unix portability path and the minimum compiler assumptions Ghostscript expected.
