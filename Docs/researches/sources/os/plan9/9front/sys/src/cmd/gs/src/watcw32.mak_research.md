# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/watcw32.mak

Watcom C++ makefile for 32-bit Windows Ghostscript builds.

Key points:
- Builds Windows GUI executable `gswin32`, console executable `gswin32c`, and DLL `gsdll32` when `MAKEDLL=1`.
- Configures build/install roots, runtime search path, debug flags, executable names, third-party sources, Watcom compiler/resource/linker paths, CPU/FPU type, and `SYNC=winsync`.
- Enables PostScript/PDF/TrueType/EPSF features and a large set of display, printer, bitmap, TIFF, PNG, JPEG, PDF/PS/PXL devices.
- Sets Windows/Watcom compile flags, including `CHECK_INTERRUPTS`, `_Windows`, `__WIN32__`, and `_WATCOM_`.
- Builds auxiliary tools with Watcom compiler/linker.
- Uses Watcom `.BEFORE` to create output directories.
- Defines object groups for small DLL loaders, large non-DLL executables, console executables, and DLL builds.
- Links either two small EXEs plus a large DLL or two large EXEs based on `MAKEDLL`.

Dependencies and interactions:
- Includes `version.mak`, `winlib.mak`, and `winint.mak`.
- Relies on generated link lists and Windows resources from shared Windows make fragments.

Research relevance:
- Primary Watcom Win32 build recipe and an important source of platform-specific output topology.
