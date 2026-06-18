# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvclib.mak

## Purpose
NMAKE makefile for building a Microsoft Visual C++ Ghostscript library/tester configuration rather than the full Windows interpreter application.

## Main Structure
- Defines runtime/install defaults, debug flags, directory defaults, third-party sources, compiler path detection, CPU/FPU settings, synchronization module, and feature/device selection.
- Sets `STDIO_IMPLEMENTATION` empty because the library build only allows normal file I/O.
- Sets `LIB_ONLY`, `MAKEDLL=0`, and `PLATFORM=mslib32_`.
- Includes `version.mak`, `msvccmd.mak`, `winlib.mak`, and `msvctail.mak`.
- Adds `gp_mslib` platform object and `mslib32_.dev`.

## Important Build Products
- `mslib32_.dev`: library platform module including `gp_mslib` and `mswin32_.dev`.
- `gslib.exe` by default: console library tester executable linked from Ghostscript library components.

## Integration Notes
- Shares most command generation and Windows library logic with `msvc32.mak`.
- Feature set is library-oriented and uses graphics-library `.dev` features rather than full interpreter Windows UI modules.

## Risks and Edge Cases
- Defaults to `TDEBUG=1` due to historical MSVC 5 optimization concerns, producing slower/larger builds.
- Supports only older MSVC versions in comments/defaults compared with `msvc32.mak`.
- Link rule manually appends required library-only objects to a trace file.
