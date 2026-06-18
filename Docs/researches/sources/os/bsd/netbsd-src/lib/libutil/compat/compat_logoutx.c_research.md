# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_logoutx.c

## Purpose
Compatibility-era implementation of `logoutx`.

## Key Details
- Looks up an existing `utmpx` entry by line.
- Updates record type and exit status fields.
- Sets timestamp with `gettimeofday`.
- Writes the updated record with `pututxline`.

## Dependencies and Role
- Similar to current `logoutx.c`; included in the requested set though not listed in the local `compat/Makefile.inc`.
