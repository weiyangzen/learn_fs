# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/watclib.mak

Watcom C/C++ makefile for MS-DOS library testing.

Key points:
- Default target builds `$(GLOBJ)gslib.exe`.
- Sets DOS-style Ghostscript root paths, runtime search path, and `GS=gslib`.
- Defaults `DEBUG`, `TDEBUG`, and `NOPRIVATE` to enabled unless overridden.
- Uses `debugobj` for generated/object/output directories by default.
- Configures bundled JPEG/libpng/zlib/JBIG2/ICC/IJS sources and `IJSEXECTYPE=win`.
- Chooses Watcom version, library paths, DOS extender stub, CPU/FPU type, and sync module.
- Includes `wccommon.mak`, `wctail.mak`, `devs.mak`, `contrib.mak`, and `winplat.mak`.
- Defines platform module `watclib_.dev` from Watcom/DOS/Win32 platform objects.
- Links `gslib.exe` with Watcom link scripts and selected library-only objects.

Dependencies and interactions:
- Uses Watcom make syntax and variables from `wccommon.mak`.
- Reuses Windows platform module rules when `WAT32` is enabled.

Research relevance:
- Legacy DOS/Watcom path for exercising Ghostscript as a graphics library rather than a standard interpreter.
