# File Research: sources/virtualization/spdk/module/event/subsystems/fsdev/Makefile

Builds the event fsdev subsystem library.

Key elements:
- Compiles `fsdev.c`.
- Produces `event_fsdev`.
- Uses shared object version `3.0`.
- Uses the blank SPDK map file.

Dependencies:
- Included only when `CONFIG_FSDEV` selects the fsdev subsystem from the parent Makefile.

Research notes:
- Provides event-framework lifecycle glue for filesystem devices.
