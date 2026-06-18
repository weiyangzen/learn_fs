# File Research: sources/virtualization/spdk/module/event/subsystems/scheduler/scheduler.c

Registers scheduler selection as an event subsystem.

Key elements:
- During init, defaults to the `static` scheduler if none is already selected.
- During fini, disables scheduler period and clears selected scheduler.
- Writes config JSON as `framework_set_scheduler` with scheduler name and optional period.
- Registers subsystem name `scheduler`.

Dependencies:
- SPDK scheduler APIs and internal event definitions.

Research notes:
- This file manages event-framework scheduler selection, not the balancing algorithm itself.
