# File Research: sources/teaching/minix/minix/drivers/storage/floppy/floppy.h

## Purpose

Provides the shared include wrapper for floppy driver source files.

## API Surface

Includes `minix/drivers.h`, `minix/blockdriver.h`, and `minix/drvlib.h`, making the block driver and MINIX driver APIs available to `floppy.c` and `liveupdate.c`.

## Dependencies

Depends only on MINIX driver headers.

## Risks

No logic is present. Its importance is keeping the live update file and main driver on the same driver API declarations.
