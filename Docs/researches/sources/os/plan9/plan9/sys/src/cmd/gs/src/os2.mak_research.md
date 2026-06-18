# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/os2.mak

Legacy Ghostscript makefile for MS-DOS or OS/2 builds using GCC/EMX or IBM C++.

It configures build directories, installation roots, runtime search paths, compiler/linker options, DLL vs EXE mode, X11 optional support, bundled JPEG/PNG/zlib/JBIG2/ICC paths, device lists, feature lists, auxiliary tools, OS/2 Presentation Manager targets, resources, icons, and packaging.

Important behavior:

- Defaults to `MAKEDLL=1`, `EMX=1`, and `USE_LARGE_COLOR_INDEX=1`.
- Configures compiler flags for GCC/EMX or IBM C++, optional debug symbols, DLL flags, CPU/FPU options, and OS/2-specific defines.
- Selects Ghostscript features such as PostScript level 3, PDF, DPS, TrueType, EPSF, and `os2print`.
- Includes generic Ghostscript build fragments plus `pcwin.mak` for Windows/OS2 device rules.
- Builds platform modules including `gp_os2`, `gp_stdia`, and OS/2 printer I/O.
- Builds auxiliary tools through EMX bind steps or IBM C++ commands.
- Supports OS/2 PM driver resources/icons and a `zip` packaging target.

This is build/platform integration for Ghostscript’s OS/2 target. It does not implement filesystem behavior, though it references OS/2 printer I/O and packaging filesystem paths.
