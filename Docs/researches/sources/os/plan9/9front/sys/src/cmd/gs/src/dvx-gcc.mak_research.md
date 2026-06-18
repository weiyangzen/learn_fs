# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-gcc.mak

## Role
Top-level GCC makefile for building Ghostscript on DesqView/X with X11 support.

## Contents
- Sets build directories (`BINDIR`, `GLSRCDIR`, `GLOBJDIR`, `PSSRCDIR`, `PSLIBDIR`, etc.) and installation paths rooted at DOS-style `c:/bin`, `c:/gs`, and `c:/gsfonts`.
- Configures install commands, default Ghostscript library path, initialization file name, generic compile options, executable name, and build-time Ghostscript.
- Selects bundled/shared dependency behavior for JPEG, PNG, zlib, jbig2dec, and icclib.
- Documents IJS as not ported to DesqView/X but still includes `ijs.mak` later.
- Sets compiler/linker variables for `gcc`, optimization flags, extra libraries, standard math library, and X11 include/library names.
- Defines platform values such as `FPU_TYPE=1`, `SYNC=posync`, file I/O mode, stdio implementation, band-list storage/compression, language feature devices, and display/output devices.
- Includes the platform head/tail makefiles and the Ghostscript component makefiles.

## Important Interfaces
- Build variables consumed by `gs.mak`, `lib.mak`, `int.mak`, `devs.mak`, `contrib.mak`, and `unix-end.mak`.
- Device lists `DEVICE_DEVS` through `DEVICE_DEVS20`.
- Feature list `FEATURE_DEVS`.

## Dependencies And Coupling
- Depends on many sibling makefiles in `$(GLSRCDIR)` and `$(PSSRCDIR)`.
- Assumes Quarterdeck DesqView/X/DJGPP-like environment, X11 libraries, DOS-style paths, and `coff2exe` behavior supplied by `dvx-tail.mak`.

## Risks And Notes
- Historical platform build file; many paths and library names are hard-coded and unlikely to work unchanged on modern systems.
- Comments call out security/confusion risks of `SEARCH_HERE_FIRST=1`, but it remains enabled.
- Includes `ijs.mak` even though the comments state IJS is not ported, which may require values to remain harmless/defaulted.

## Filesystem Relevance
Build-system only. It controls installation and runtime search paths but does not implement filesystem code.
