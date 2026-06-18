# File Research: sources/teaching/minix/minix/drivers/storage/floppy/Makefile

## Purpose

Builds the MINIX floppy disk service.

## Build Role

Defines `PROG=floppy` with sources `floppy.c` and `liveupdate.c`. Links against `libblockdriver`, `libsys`, and `libtimers`, then includes `minix.service.mk` to build/install it as a MINIX service.

## Dependencies

The service depends on block driver support, low-level system calls, and MINIX timer helpers.

## Risks

The Makefile is simple; build correctness mostly depends on keeping `liveupdate.c` linked with `floppy.c` because the main driver declares live update callbacks externally.
