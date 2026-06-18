# File Research: sources/teaching/minix/minix/drivers/storage/ahci/Makefile

## Purpose
Builds the AHCI storage service.

## Key Behavior
- Defines `PROG= ahci`.
- Builds from `ahci.c`.
- Links against `libblockdriver`, `libsys`, `libtimers`, and `libmthread`.
- Includes `<minix.service.mk>` to build it as a MINIX service.

## Integration Notes
The `libblockdriver_mt` usage in `ahci.c` requires `libmthread`; timers are used for port and command timeouts.

## Risks
Removing `libmthread` or `libtimers` would break the multithreaded command and timeout model.
