# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus.h

Read completely: 695 lines.

This header defines DragonFlyBSD's kernel bus/device framework API.

Key contents:
- Core opaque types: `device_t`, `driver_t`, `devclass_t`, and interrupt handler typedefs.
- User-exported bus/device info structures.
- Device state enum and interrupt feature/trigger/polarity constants.
- Resource list entry/list definitions and resource-list helper prototypes.
- Root bus and generic bus method prototypes for attach/detach/probe, resource allocation, ivars, interrupts, suspend/resume/shutdown, and child management.
- Public bus resource wrappers, device accessors/mutators, devclass APIs, resource configuration APIs, and bus generation tracking.
- Driver/module macros for registering drivers on buses.
- Generic ivar accessor-generation macro.
- Bus-space convenience macros for 1/2/4/8-byte read/write, multi, region, set, stream, and barriers through `struct resource`.

Important interactions:
- Includes generated `device_if.h` and `bus_if.h`.
- Integrates with `bus_dma.h`, `bus_resource.h`, kobj methods, sysctl, config resources, and driver modules.

Security/reliability notes:
- This is a broad kernel driver ABI. Mismatched resource ownership, interrupt setup/teardown, or ivar IDs can destabilize device attach/detach paths.
- Probe priority constants are currently all zero except `BUS_PROBE_SPECIFIC`, so drivers cannot rely on nuanced priority ordering here.
