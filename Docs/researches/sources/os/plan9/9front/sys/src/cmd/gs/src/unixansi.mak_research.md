# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixansi.mak

Top-level portable Unix/ANSI C/X11 Ghostscript makefile.

Key points:
- Mirrors the Unix build layout from `unix-gcc.mak` but avoids GCC-specific assumptions.
- Leaves `CC` to the platform unless an ANSI-compatible compiler must be specified.
- Uses simpler flags: standard `-O`, debug `-g`, profile `-pg -O`, and generic `XCFLAGS`.
- Configures runtime/install directories, bundled JPEG/libpng/zlib/JBIG2/ICC/IJS source directories, X11 paths, `FPU_TYPE=1`, and `SYNC=nosync`.
- Enables PostScript Level 3, PDF, DPS, TrueType font support, EPSF, pipe, and FAPI.
- Device list is narrower than `unix-gcc.mak`, though it still includes X11 devices, printers, raster outputs, TIFF/PNG/JPEG, PDF/PS/PXL writers, and bbox.
- Includes Unix head, graphics library, interpreter, compiled fonts, image libraries, ICC/IJS, devices, contrib, Unix auxiliary/link/end/install fragments.
- Provides `distclean` and `maintainer-clean`.

Dependencies and interactions:
- Depends on the same generic Ghostscript make fragments as the GCC file but omits `unix-dll.mak`.
- Uses `CC_NO_WARN=$(CC_)` rather than GCC warning suppression.

Research relevance:
- Shows the portable Unix build path for non-GCC ANSI compilers and provides a contrast with the GCC/X11 build profile.
