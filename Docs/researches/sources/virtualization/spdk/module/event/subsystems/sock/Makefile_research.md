# File Research: sources/virtualization/spdk/module/event/subsystems/sock/Makefile

Builds the event sock subsystem library.

Key elements:
- Compiles `sock.c`.
- Produces `event_sock`.
- Uses shared object version `7.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- Initializes socket implementations used by networked targets such as NVMe-oF and iSCSI.
