# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/expand.h

## Purpose
Small header for the decompressor/tiny boot environment.

## Main Interfaces
- Defines `ROUND`, `PGROUND`, `HOWMANY`, and `ROUNDUP`.
- Declares `cgainit`, `cgaputc`, `inb`, and `outb`.

## Implementation Notes
- Replaces normally available Plan 9 kernel rounding macros for the standalone decompressor.
- Provides just enough declarations for `expand.c` and `cga.tiny.c`.

## Dependencies And Risks
- Must stay consistent with `mem.h` page size and the assembly I/O helpers.
