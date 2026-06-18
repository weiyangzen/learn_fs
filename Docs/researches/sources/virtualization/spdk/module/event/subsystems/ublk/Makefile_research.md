# File Research: sources/virtualization/spdk/module/event/subsystems/ublk/Makefile

Builds the event ublk subsystem library.

Key elements:
- Compiles `ublk.c`.
- Produces `event_ublk`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by the parent Makefile when Linux and `CONFIG_UBLK=y`.

Research notes:
- Runtime dependencies are bdev and iobuf.
