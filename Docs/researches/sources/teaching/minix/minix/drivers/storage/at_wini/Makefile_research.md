# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/Makefile

## Purpose
Builds the legacy AT Winchester/ATA storage service.

## Key Behavior
- Defines `PROG= at_wini`.
- Builds from `at_wini.c` and `liveupdate.c`.
- Links against `libblockdriver`, `libsys`, and `libtimers`.
- Includes `<minix.service.mk>`.

## Integration Notes
The driver uses the synchronous blockdriver interface plus SEF live update callbacks supplied by `liveupdate.c`.

## Risks
The live update object is part of the service contract; omitting it would remove custom readiness states for in-flight ATA commands.
