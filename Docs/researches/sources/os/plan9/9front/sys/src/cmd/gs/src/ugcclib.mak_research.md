# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ugcclib.mak

Unix/gcc makefile for Ghostscript graphics-library testing rather than the full interpreter.

Key points:
- Builds into `./libobj`, names the output `gslib`, and includes `version.mak`.
- Configures Ghostscript runtime paths, init file, feature devices, device list, bundled JPEG/libpng/zlib/JBIG2/ICC/IJS settings, compiler flags, X11 paths, and platform options.
- Uses `gcc`, `ar`, and `ranlib`; defaults to debug-style `CFLAGS_DEBUG`.
- Includes core fragments: `unixhead.mak`, `gs.mak`, `lib.mak`, image/ICC/IJS makefiles, `devs.mak`, `contrib.mak`, and `unix-aux.mak`.
- Replaces the standard `unixlink.mak` final link with custom rules for `$(GS_XE)` and `libgsgraph.a`.
- The final link builds from `gslib.o`, selected no-GC/config objects, library objects, and device objects.

Dependencies and interactions:
- Depends on generated link scripts from the generic Ghostscript make system.
- Shares Unix platform modules from `unix-aux.mak`.
- Includes `unix-end.mak` for standard directory/debug/profile support.

Research relevance:
- Useful for distinguishing full Ghostscript interpreter builds from library-only testing builds in the old source tree.
