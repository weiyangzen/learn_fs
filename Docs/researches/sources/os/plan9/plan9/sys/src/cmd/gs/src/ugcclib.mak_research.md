# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ugcclib.mak

Unix/gcc makefile for Ghostscript graphics library testing.

Key points:
- Builds in `./libobj`, names output `gslib`, and uses `version.mak`.
- Configures Ghostscript library/resource/font search paths under `/usr/local/share/ghostscript`.
- Uses gcc with warnings and debug flags by default; links against `-lm` plus optional X11 libraries.
- Chooses mostly library features such as DPS, PostScript level libraries, CIE, path, pattern, halftone, raster-op, and CMap support.
- Defines device list centered on X11, basic PNM/PBM/PGM/PPM devices, `djet500`, `bitcmyk`, and `bbox`.
- Includes common make fragments for core library, JPEG, zlib, libpng, JBIG2, icclib, ijs, devices, contrib, and Unix auxiliary rules.
- Replaces `unixlink.mak` with custom link/archive rules for `$(GS_XE)` and `libgsgraph.a`.

Dependencies and interactions:
- Depends on many shared make fragments and generated trace files from `echogs`.
- Uses `unix-aux.mak` and `unix-end.mak` but not the standard interpreter link path.

Research relevance:
- Specialized Unix gcc build target for library-oriented Ghostscript testing rather than the normal interpreter executable.
