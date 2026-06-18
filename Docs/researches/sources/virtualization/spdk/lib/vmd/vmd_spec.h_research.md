# File Research: sources/virtualization/spdk/lib/vmd/vmd_spec.h

## Purpose

Defines VMD/PCI/PCIe constants and register-layout structs used by the VMD implementation for direct PCI config-space access.

## Key Contents

- VMD limits and signatures:
  - `MAX_VMD_SUPPORTED`
  - `VMD_UPPER_BASE_SIGNATURE`
  - `VMD_UPPER_LIMIT_SIGNATURE`
- VMD config registers:
  - `PCI_VMD_VMCAP`
  - `PCI_VMD_VMCONFIG`
- PCI BAR, bridge, bus, class, command, and capability constants.
- Hotplug and memory-window constants:
  - `ADDR_ELEM_COUNT`
  - `PCI_MAX_BUS_NUMBER`
  - `RESERVED_HOTPLUG_BUSES`
  - `BAR_SIZE`
- PCI capability layouts:
  - enhanced capability header
  - serial number capability
  - common/type-0/type-1 PCI headers
  - MSI and MSI-X capability/table structs
  - PCIe capability unions for slot/link/root registers
- `struct pci_header` union wrapper for common/type-0/type-1 access.

## Relationships

- Included by `vmd_internal.h`, then used throughout `vmd.c`.
- Provides the raw register views that `vmd.c` casts over MMIO config space.

## Notes

- This is hardware ABI-style code; field order and widths are critical.
- Macros such as `CONFIG_OFFSET_ADDR` encode VMD config-space addressing assumptions.
