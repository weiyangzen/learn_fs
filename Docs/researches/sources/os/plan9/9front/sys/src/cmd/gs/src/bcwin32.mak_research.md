# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/bcwin32.mak

This is the Borland C++ Windows makefile for Ghostscript. It supports Win32 graphical and console builds, optional DLL layout, setup/uninstall utilities, and some 16-bit spooler integration for older Windows paths.

Key responsibilities:
- Defines Ghostscript build directories and Windows install roots such as `AROOTDIR`, `GSROOTDIR`, and `GS_DOCDIR`.
- Configures runtime search paths in Windows form via `GS_LIB_DEFAULT`.
- Sets executable names: `gswin32`, `gswin32c`, and `gsdll32`.
- Controls debug, test-debug, private-symbol exposure, DLL mode, and multithread builds with `DEBUG`, `TDEBUG`, `NOPRIVATE`, `MAKEDLL`, and `MULTITHREAD`.
- Defines bundled library source directories for JPEG, libpng, zlib, icclib, and IJS.
- Detects/sets Borland compiler family paths for old Borland C++ and C++Builder versions.
- Selects Windows device groups, including display, printer, bitmap, TIFF, PNG, JPEG, PDF/PS writers, and other raster devices.
- Includes `winlib.mak` and `winint.mak` for shared Windows library/interpreter build logic.

Important build relationships:
- Generates a compiler response file `ccf32.tr`.
- Builds auxiliary tools such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- In `MAKEDLL` mode, builds small graphical and console loaders plus the large `gsdll32.dll`.
- In non-DLL mode, builds larger standalone graphical and console executables.
- Contains setup and uninstall program rules when DLL builds are enabled.
- Contains conditional legacy spooler build rules for `gs16spl.exe`.

Notable implementation details and risks:
- The makefile is tailored to historical Borland Windows toolchains and old Windows compatibility layers.
- Uses Windows/Borland make syntax, not POSIX make or Plan 9 mk.
- The conditional near the 16-bit spooler section reads `!if $(BUILDER_VERSION !=5)`, which looks syntactically suspicious compared with earlier `!if $(BUILDER_VERSION) !=5`.
- No filesystem implementation logic is present. It manipulates files only as build artifacts through compiler/linker/resource rules.

Research classification: Windows Borland Ghostscript build orchestration, relevant for portability and device dependency mapping.
