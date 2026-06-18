# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/Makefile.in

This is the autoconf `Makefile` template for building Ghostscript on Unix-like platforms.

Core responsibilities:
- Defines source, generated, object, binary, library, documentation, example, and install directories.
- Sets runtime search paths such as `GS_LIB_DEFAULT` and cache path `GS_CACHE_DIR`.
- Captures configurable build settings substituted by `configure`: compiler, CFLAGS, library paths, X11 flags, external library locations, and optional devices.
- Selects Ghostscript language features and output devices.
- Chooses whether to compile PostScript initialization files into the executable.
- Sets band-list storage/compression, file I/O implementation, stdio implementation, synchronization backend, and floating-point assumptions.
- Includes the real build fragments: `unixhead.mak`, `gs.mak`, `lib.mak`, `int.mak`, `cfonts.mak`, `jpeg.mak`, `zlib.mak`, `libpng.mak`, `jbig2.mak`, `jasper.mak`, `icclib.mak`, `ijs.mak`, `devs.mak`, `contrib.mak`, and Unix link/install tails.

Important build dependencies:
- JPEG, zlib, libpng, JBIG2, JasPer, ICC, and IJS support are controlled through substituted `@...@` variables.
- PNG devices are populated through `@PNGDEVS@`.
- X11 devices are populated through `@X11DEVS@`.

Targets:
- `distclean` removes generated build outputs and configure byproducts.
- `maintainer-clean` also removes autotools-generated inputs.
- `check` aliases to `default` and then no-ops.

Filesystem relevance is build-time only: it defines installation layout and search paths, but does not implement runtime filesystem logic.
