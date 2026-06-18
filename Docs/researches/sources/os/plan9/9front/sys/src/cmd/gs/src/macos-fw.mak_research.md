# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-fw.mak

## Purpose
Partial makefile for Mac OS X/Darwin shared library and framework targets.

## Main Structure
- Defines shared-object output directories `SOOBJRELDIR` and `SOBINRELDIR`.
- Defines simple loader executable names, dylib names, soname variants, and symlink rules.
- Defines `SODEFS` to run recursive make with dynamic-library linker flags and separate generated/object directories.
- Provides `so`, `sodebug`, `install-so`, `soinstall`, `framework`, `framework_install`, `SODIRS`, and `soclean` targets.

## Important Build Products
- Dylib names: `lib$(GS).dylib`, major, and major/minor variants.
- Loader executable: `$(GS)c$(XE)` built from `dxmainc.c`.
- Framework tree under `$(BINDIR)/../sobin/$(FRAMEWORK_NAME).framework`.

## Integration Notes
- Included by `macosx.mak`.
- Framework packaging copies public headers `iapi.h`, `ierrors.h`, `gdevdsp.h`, `Info-macos.plist`, `lib`, `man`, `doc`, and the built dylib into the framework layout.

## Risks and Edge Cases
- Comments note the install name is framework-oriented and can make plain `.dylib` usage secondary or broken.
- Uses `rm -rf` for framework rebuild/install paths; prefix values must be correct.
- Symlink rules assume Unix-like filesystem semantics.
