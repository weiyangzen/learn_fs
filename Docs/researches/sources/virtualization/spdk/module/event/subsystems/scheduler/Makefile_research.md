# File Research: sources/virtualization/spdk/module/event/subsystems/scheduler/Makefile

Builds the event scheduler subsystem library.

Key elements:
- Compiles `scheduler.c`.
- Produces `event_scheduler`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- Separate scheduler implementations are under `module/scheduler`.
