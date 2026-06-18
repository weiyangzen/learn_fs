# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macosx.mak

## Purpose
Mac OS X/Darwin GCC/framework Ghostscript configuration makefile.

## Main Structure
- Defines build directories, install commands, framework paths, runtime resource/font paths, Ghostscript executable name, build-time Ghostscript, and third-party source/library options.
- Sets Darwin-oriented compiler/linker flags, default devices, features, band-list storage, file/stdio implementation, and synchronization mode.
- Includes Unix/Ghostscript partial makefiles, third-party makefiles, device/contrib makefiles, `macos-fw.mak`, and Unix install tail.

## Important Defaults
- Framework prefix: `/Library/Frameworks/Ghostscript.framework`.
- `GS_LIB_DEFAULT` includes framework resources plus `/Library/Fonts` and `/System/Library/Fonts`.
- `CAPOPT=-DHAVE_MKSTEMP`.
- `SHARE_ZLIB=1`; JPEG, PNG, JBIG2 use bundled builds by default.
- Default output devices emphasize PNG output plus PNM/JPEG/PDF/PS/PXL/bbox.

## Integration Notes
- `macos-fw.mak` supplies shared-library/framework targets.
- Uses normal Unix-style build fragments, unlike `macos-mcp.mak` which generates CodeWarrior project XML.

## Risks and Edge Cases
- `SYNC=nosync` by default even on Darwin unless changed.
- X11 variables are empty by default.
- Framework resource layout is encoded in make variables and packaging rules, so version/path changes affect runtime lookup.
