# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nexusdefs.h

## Purpose

`nexusdefs.h` defines shared DDI bus nexus operation enumerations. It is a small ABI-style header used by nexus and child drivers to classify control operations, bus configuration requests, and power-management notifications.

## Main Interfaces

`ddi_ctl_enum_t` enumerates bus nexus control operations including DMA mapping setup, child init/uninit, device and interrupt reporting, register sizing, affinity, I/O minimum, page/block conversions, power, attach/detach, quiesce/unquiesce, peek, and poke. Several obsolete operation numbers are preserved as `DDI_CTLOPS_RESERVED*` entries to maintain numeric compatibility.

`DDI_CTLOPS_REMOVECHILD` aliases `DDI_CTLOPS_UNINITCHILD` for old source compatibility.

`ddi_bus_config_op_t` defines bus enumeration/configuration/unconfiguration operations: enumerate, one/all/AP/driver config, one/driver/all/AP unconfig, and OBP argument-based config.

`pm_bus_power_op_t` defines bus power notifications and operations such as child power-change, nexus power-up, pre/post notification, has-changed, and no-involvement.

## Runtime Use

There is no executable logic. These enum values are consumed by bus framework callbacks and driver switch implementations to dispatch operation-specific behavior.

## Dependencies

The header is self-contained apart from C++ linkage guards.

## Risks and Invariants

The enum order is part of the interface. The reserved obsolete slots must not be collapsed or renumbered because existing compiled code and source assumptions may depend on historical numeric values.
