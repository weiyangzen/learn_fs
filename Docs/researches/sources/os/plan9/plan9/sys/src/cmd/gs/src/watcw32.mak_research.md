# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/watcw32.mak

Watcom C++ makefile for 32-bit Windows Ghostscript.

Key points:
- Builds Windows GUI `gswin32`, console `gswin32c`, and DLL `gsdll32` by default with `MAKEDLL=1`.
- Sets install/runtime roots under `c:/gs/gs$(GS_DOT_VERSION)`.
- Configures Watcom tool paths from `%WATCOM%`, CPU/FPU flags, Windows resource compiler, linker, and `SYNC=winsync`.
- Defines language features: PostScript Level 3, PDF, DPS Next, TrueType fonts, and EPSF.
- Defines Windows/default devices plus printer, bitmap, fax, PCX, PBM/PNM/PPM, TIFF, PNG, JPEG, PDF/PS/PXL writer, and other device groups.
- Includes `version.mak`, `winlib.mak`, and `winint.mak`.
- Generates `ccf32.tr` compiler response file with Windows and Watcom defines.
- Builds auxiliary tools, creates directories via Watcom `.BEFORE`, compiles `gp_mktmp`, and links either small EXE loaders plus big DLL or large standalone EXEs.

Dependencies and interactions:
- Uses common Windows interpreter/resource rules from `winint.mak`.
- Uses platform and library modules from `winlib.mak`/`winplat.mak`.

Research relevance:
- Full legacy 32-bit Windows Watcom build configuration, including DLL-vs-standalone linking structure.
