# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_private.h

Read completely: 148 lines.

This private kernel header defines internal bus/device framework structures.

Key contents:
- Rejects inclusion from userland.
- `driverlink` entries for drivers attached to devclasses.
- TAILQ list typedefs for devclasses, drivers, and devices.
- `struct devclass` with parent, drivers, name, unit-indexed device array, max unit, and sysctl state.
- Config resource/device structures for config-provided integers, strings, and longs.
- `struct bsd_device` implementation with kobj fields, parent/child/global links, driver/devclass/unit/name/description, busy count, state, flags, ivars, softc, and sysctl state.
- Internal device flags for enablement, fixed class, wildcard unit, malloced description, quiet attach, no-match state, external softc, and async probe.
- `struct device_op_desc` method metadata.

Security/reliability notes:
- Internal layout is tightly coupled to `kern/subr_bus.c`-style implementation and kobj dispatch.
- Incorrect manipulation of flags, child lists, or sysctl contexts can break hotplug and driver lifecycle behavior.
