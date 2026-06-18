# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wccommon.mak

Common Watcom C/C++ makefile section for DOS and Windows builds.

Key points:
- Documents required parameters supplied by Watcom platform makefiles.
- Uses `.NOCHECK` and extends suffixes for Watcom make behavior.
- Disables shared third-party libraries: JPEG, libpng, zlib, and JBIG2 are built in.
- Defines DOS/Watcom command, object, executable, include, define, output, and path syntax.
- Provides batch-file wrappers for copy/remove commands.
- Selects Watcom compiler, linker, stub, and resource compiler based on `WCVERSION`, including hosted Win95/NT variants.
- Sets include directories and whether tools are 32-bit-hosted (`WAT32`).
- Normalizes FPU defaults based on CPU type.
- Defines assembler suffix rule and default `dosdefault`.
- Constructs debug/privacy/optimization flags and compiler command variables `CC`, `CCAUX`, `CC_`, `CC_D`, `CC_INT`, and `CC_NO_WARN`.

Dependencies and interactions:
- Included by `watclib.mak` and related Watcom makefiles.
- Feeds `wctail.mak` and generic Ghostscript fragments with platform syntax.

Research relevance:
- Core Watcom portability layer for old DOS/Windows Ghostscript builds.
