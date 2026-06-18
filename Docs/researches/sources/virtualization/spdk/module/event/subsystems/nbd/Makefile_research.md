# File Research: sources/virtualization/spdk/module/event/subsystems/nbd/Makefile

Builds the event NBD subsystem library.

Key elements:
- Compiles `nbd.c`.
- Produces `event_nbd`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Included only from the parent subsystem Makefile on Linux.

Research notes:
- Runtime dependency on bdev is declared in the C file.
