# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-tail.mak

## Role
Common final makefile fragment for DesqView/X Ghostscript builds.

## Contents
- Uses `.NOEXPORT` to avoid oversized inherited environment argument lists.
- Defines the DesqView/X platform device `dvx_.dev` from platform object files and `nosync.dev`.
- Provides rules for compiling `gp_dvx.c` with `-D__DVX__` and `gp_stdin.c`.
- Provides auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, compiling with GCC, stripping, converting COFF to `.exe`, and deleting intermediate executables.
- Generates `gconfig_.h` with `echogs`, defining `HAVE_SYS_TIME_H` and `HAVE_DIRENT_H`.
- Defines final interpreter link rule for `$(GS_XE)` using `ld.tr`, object/library/device lists, extra libraries, and `coff2exe`.

## Important Interfaces
- Target `$(GLGEN)dvx_.dev`.
- Targets for Ghostscript auxiliary executables.
- Target `$(gconfig__h)`.
- Target `$(GS_XE)`.

## Dependencies And Coupling
- Depends on objects and generated variables from Ghostscript generic makefiles.
- Requires platform tools `strip`, `coff2exe`, and DOS `del`.
- Assumes `/djgpp/include` for `INCLUDE`.

## Risks And Notes
- Legacy DOS/DVX build rules are brittle outside the intended toolchain.
- The platform device includes both DOS/unix-ish filesystem glue objects (`gp_unifs`, `gp_dosfs`) alongside DV/X glue.

## Filesystem Relevance
Build glue references filesystem platform objects but contains no filesystem implementation.
