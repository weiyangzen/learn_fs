# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvc32.mak

## Purpose
Primary NMAKE makefile for 32-bit/64-bit Microsoft Visual C++ Ghostscript executable and DLL builds on Windows.

## Main Structure
- Defines configurable directories, install paths, runtime library path, debug/release flags, executable/DLL names, third-party source directories, build-time Ghostscript, and `MAKEDLL`.
- Detects or defaults MSVC versions 4 through 8 and sets compiler, linker, resource compiler, include, and library directories.
- Defines CPU/FPU options, synchronization module, feature/devices, large color-index support, and UFST flags.
- Includes `msvccmd.mak`, `winlib.mak`, `msvctail.mak`, and `winint.mak`.
- Provides link rules for DLL-based small GUI/console loaders or large standalone GUI/console executables.

## Important Build Products
- GUI executable: `gswin32.exe` by default.
- Console executable: `gswin32c.exe`.
- DLL: `gsdll32.dll`.
- Setup/uninstall executables when `MAKEDLL=1`.
- Response files such as `lib32.rsp` and `gswin32.rsp`.

## Integration Notes
- Uses `winlib.mak` and `winint.mak` for Windows platform and interpreter object sets.
- `DEBUGDEFS` target recursively builds debug variants in separate directories.

## Risks and Edge Cases
- Many version/path defaults are historical and target old Visual Studio layouts.
- 64-bit support relies on DDK/VS-specific paths and conditionals.
- Conditional near the default target check uses `Win64` casing while most later logic uses `WIN64`, which may affect defaulting behavior depending on NMAKE definitions.
- Link steps rely on generated response files and cleanup commands; failed intermediate steps may leave stale `.rsp`/`.tr` files.
