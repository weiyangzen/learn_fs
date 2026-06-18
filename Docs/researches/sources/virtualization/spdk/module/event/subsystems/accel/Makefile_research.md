# File Research: sources/virtualization/spdk/module/event/subsystems/accel/Makefile

Builds the event accel subsystem library.

Key elements:
- Compiles `accel.c`.
- Produces `event_accel`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Depends on SPDK common and library make fragments.

Research notes:
- Runtime dependency on iobuf is declared in the corresponding C file.
