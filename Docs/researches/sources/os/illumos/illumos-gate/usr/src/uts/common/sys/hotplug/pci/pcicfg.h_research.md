# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/pci/pcicfg.h

## Role

`pcicfg.h` declares the PCI configurator module interface used to configure and unconfigure PCI devices during hotplug and boot-time enumeration.

## Key Interfaces and Data

- `pcicfg_flags_t` includes read-only probing mode and ARI enable mode.
- Declares `pcicfg_configure()` and `pcicfg_unconfigure()` with nexus devinfo, device/function selectors, and flags.
- Defines success/failure aliases to `DDI_SUCCESS` and `DDI_FAILURE`.
- `PCICFG_ALL_FUNC` selects all functions.
- Defines non-transparent bridge subclass `PCI_BRIDGE_STBRIDGE`.
- Defines config access mapping constants for indirect and direct maps.

## Dependencies and Use

This is a small kernel module boundary for PCI hotplug/configuration consumers.

## Research Notes

The flags reveal two special flows: virtual hotplug where probing is avoided, and boot-time ARI enablement.
