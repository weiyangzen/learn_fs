# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-gcc.mak

Primary Unix/gcc/X11 Ghostscript makefile.

Key points:
- Sets build directories, install paths, runtime resource paths, `GS=gs`, and `BUILD_TIME_GS=gs`.
- Enables `CAPOPT=-DHAVE_MKSTEMP`.
- Configures bundled third-party libraries: JPEG 6, libpng 1.2.8, zlib, jbig2dec, icclib, and ijs.
- Uses gcc with strict warnings, `-fno-builtin`, `-fno-common`, standard/debug/profile/SO flags, and `GX_COLOR_INDEX_TYPE='unsigned long long'`.
- Defaults to `SYNC=nosync` and `STDLIBS=-lm`.
- Configures X11 include/lib paths under `/usr/X11R6`.
- Enables language features including PostScript Level 3, PDF, DPS Next, TrueType fonts, EPSF, pipe, and FAPI.
- Defines extensive device sets: X11 devices, BMP, Epson/HP/Canon printer drivers, fax, PCX, PBM/PNM/PPM, TIFF, PNG, JPEG, PDF/PS/PXL writers, `bbox`, spot/devicen/XCF, and others.
- Includes Unix core fragments plus `unixlink.mak`, `unix-dll.mak`, `unix-end.mak`, and `unixinst.mak`.
- Generates `cc.tr` to work around gcc 2.7 const optimizer behavior.

Dependencies and interactions:
- Main top-level makefile for Unix gcc manual builds.
- Pulls in interpreter, library, device, contrib, install, and shared-library rules.

Research relevance:
- Canonical legacy Unix gcc build configuration for the Ghostscript tree in this Plan 9 source import.
