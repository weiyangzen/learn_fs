# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/configure.ac

This is the autoconf input for generating Ghostscript’s Unix `configure` script.

Key responsibilities:
- Initializes autoconf with `AC_INIT`, requires autoconf 2.52, and uses `src/gs.c` as the source marker.
- Detects C compiler, preprocessor, and ranlib.
- Tests supported compiler optimization and warning flags, adding them to `OPT_CFLAGS` and `GCFLAGS`.
- Checks headers, typedefs, structures, time handling, stdint availability, and 64-bit integer types for `GX_COLOR_INDEX_TYPE`.
- Detects math library support and required support libraries.
- Locates JPEG, zlib, PNG, IJS, JBIG2, JasPer, and X11 support.
- Substitutes selected library source/shared settings into `Makefile.in`.
- Defines optional build features such as compiled initialization files and Ghostscript executable naming.
- Checks library functions like `mkstemp`, `hypot`, `fork`, `malloc`, `memcmp`, `stat`, `vprintf`, and assorted libc routines.

Important dependency behavior:
- JPEG is required. Local source is preferred so Ghostscript’s `D_MAX_BLOCKS_IN_MCU` patch can apply.
- zlib is required for level 3 and libpng support.
- PNG output devices are enabled only when local libpng source or a usable shared libpng/header is found.
- IJS, JBIG2, JasPer, and X11 are optional and adjust device lists accordingly.
- JasPer local source may trigger its own `configure` or `autogen.sh`.

Notable implementation details and risks:
- Uses older autoconf macros such as `AC_TRY_COMPILE`.
- Several messages and comments reflect historical spelling/wording issues, but behavior is clear.
- This is build feature detection, not runtime logic.
- It directly controls whether the `pngwutil.c` libpng writer participates in the build through `SHARE_LIBPNG`, `LIBPNGDIR`, and `PNGDEVS`.

Research classification: Ghostscript Unix configure source, central to optional library/device selection.
