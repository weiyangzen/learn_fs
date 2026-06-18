# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/memory_.h

## Purpose
Ghostscript portability wrapper for memory/string routines such as `memcpy`, `memcmp`, `memmove`, `memset`, and `memchr`.

## Main Structure
- Includes `std.h` first.
- Handles Turbo C, VMS, POSIX/STDC, HP-UX, Watcom, THINK C, BSDI, FreeBSD, MSVC, old BSD, UTEK, System V, and Sun variants.
- Defines `memcmp_inline`.
- Maps missing or profiling-substituted routines to Ghostscript implementations: `gs_memmove`, `gs_memcpy`, `gs_memset`, `gs_memchr`.

## Integration Notes
- Used widely across `lib.mak` object dependencies.
- Replacement implementations are declared here and supplied elsewhere, noted as `gsmisc.c` for missing routines.

## Risks and Edge Cases
- Old BSD `bcmp` semantics differ from `memcmp`; comment warns it may return only zero/non-zero.
- Profiling mode replaces standard memory functions even if the platform supplies them.
