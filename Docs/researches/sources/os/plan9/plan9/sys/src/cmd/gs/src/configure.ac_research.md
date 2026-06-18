# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/configure.ac

This is the autoconf input used to generate the Unix `configure` script for Ghostscript.

Core responsibilities:
- Initializes autoconf, locates C compiler/preprocessor/ranlib, and probes supported compiler optimization/warning flags.
- Checks system headers, typedefs, structures, `const`, `inline`, size types, time structures, and stdint-style integer types.
- Adds selected defines to `GCFLAGS`, including `HAVE_STDINT_H`, `SYS_TYPES_HAS_STDINT_TYPES`, `const=`, and a detected 64-bit `GX_COLOR_INDEX_TYPE`.
- Checks math library support and many libc/system functions.
- Finds required JPEG support from local source directories or system lib/header.
- Finds zlib from local source or system lib/header.
- Finds libpng and enables PNG output devices if local/system PNG support is available.
- Optionally enables IJS, JBIG2, JasPer/JPEG2000, and X11 devices.
- Provides `--with-gs=NAME` and `--enable-compile-inits`.
- Substitutes variables consumed by `Makefile.in`.

Important device variables:
- `PNGDEVS_ALL` includes PNG output devices such as `png48`, `png16m`, `pnggray`, `pngmono`, `png256`, `png16`, and `pngalpha`.
- `X11DEVS` is populated only when X11 is found.
- `JBIG2DEVS` and `JPXDEVS` are conditional on library availability and feature settings.

Filesystem relevance:
- Mostly configure-time probing of local source directories and system headers/libraries.
- It affects build inclusion of PNG/JPEG/PDF/image features but implements no runtime file access.
