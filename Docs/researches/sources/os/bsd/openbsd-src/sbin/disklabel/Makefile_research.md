# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/Makefile

## Purpose
This Makefile builds the OpenBSD `disklabel` utility.

## Main Contents
- Sets `PROG=disklabel`.
- Builds sources `disklabel.c`, `dkcksum.c`, `editor.c`, and generated `manual.c`.
- Links against `libutil`.
- Installs manuals `disklabel.8` and `disklabel.5`.
- Generates `manual.c` from the rendered `disklabel.8` manual compressed through gzip and emitted as a C byte array.
- Provides a `NOMAN` fallback that embeds compressed text saying `no manual`.
- Adds sparc64-specific `SUN_CYLCHECK` and `SUN_AAT0` compile definitions.

## Integration Notes
`manual.c` is a generated build artifact consumed by the interactive editor/manual path outside the listed files.
