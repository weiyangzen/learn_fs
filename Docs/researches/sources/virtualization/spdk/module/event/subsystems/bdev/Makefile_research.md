# File Research: sources/virtualization/spdk/module/event/subsystems/bdev/Makefile

Builds the event bdev subsystem library.

Key elements:
- Compiles `bdev.c`.
- Produces `event_bdev`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- This is the build wrapper for block device framework lifecycle integration.
