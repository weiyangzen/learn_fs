# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvccmd.mak

## Purpose
Common MSVC command/flag definition fragment for Ghostscript Windows builds.

## Main Structure
- Sets MSVC-version-specific linker/compiler quirks such as `/QI0f` and `CCAUX_TAIL`.
- Defines path separator, shell macro, object/compiler switches, and genconf arguments.
- Provides `dosdefault` target to make the default target work under DOS/NMAKE conventions.
- Defines warning, CPU, FPU, debug, optimization, stack-check, precompiled-header, include, and runtime-library flags.
- Constructs `CC`, `CPP`, `CC_`, `CC_D`, `CC_INT`, `CC_NO_WARN`, `CCAUX`, and `CCWINFLAGS`.

## Integration Notes
- Included by `msvc32.mak` and `msvclib.mak`.
- Depends on variables such as `MSVC_VERSION`, `CPU_FAMILY`, `FPU_TYPE`, `DEBUG`, `TDEBUG`, `DEBUGSYM`, `MAKEDLL`, and generated `ccf32.tr`.

## Risks and Edge Cases
- Optimization settings encode historical MSVC 5 compiler bug workarounds.
- Debug/release runtime library flags switch between `/MT`, `/MTd`, and symbol options.
- Modern MSVC behavior may differ substantially from these legacy assumptions.
