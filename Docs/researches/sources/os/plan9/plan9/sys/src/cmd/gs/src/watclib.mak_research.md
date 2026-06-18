# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/watclib.mak

Watcom C/C++ makefile for MS-DOS library testing.

Key points:
- Default target builds `$(GLOBJ)gslib.exe`.
- Defaults to debug-oriented settings: `DEBUG=1`, `TDEBUG=1`, `NOPRIVATE=1`.
- Uses `GS=gslib`, output directories under `.\debugobj`, and runtime paths under `c:/gs/gs$(GS_DOT_VERSION)`.
- Configures JPEG/libpng/zlib/JBIG2/icclib/ijs source roots.
- Selects Watcom version/toolchain, CPU/FPU type, library paths, DOS extender stub, and default sync.
- Includes `wccommon.mak`, `wctail.mak`, device/contrib makefiles, and `winplat.mak`.
- Builds `watclib_.dev` from `gp_getnv`, `gp_iwatc`, and either DOS filesystem/platform objects or Windows platform include depending on `WAT32`.
- Defines link-response generation and final `gslib.exe` link using `wlink`.

Dependencies and interactions:
- Shares Watcom common rules with other DOS/Windows Watcom builds.
- Uses `winplat.dev` when building with 32-bit Watcom tools.

Research relevance:
- Historical Watcom DOS library-test build path.
