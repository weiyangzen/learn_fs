# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/plat/pci_prd.h

## Purpose
Defines the platform PCI Resource Discovery interface used by generic PCI enumeration to discover platform-specific root complexes, resource windows, slot names, and compatibility behavior.

## Main Interfaces
- `pci_prd_rsrc_t`: resource types for I/O ports, MMIO, prefetchable memory, and PCI buses.
- `pci_prd_upcalls_t`: upcall table, currently `pru_bus2dip_f`.
- Lifecycle:
  - `pci_prd_init()`
  - `pci_prd_fini()`
- Discovery:
  - `pci_prd_max_bus()`
  - `pci_prd_find_resource()`
  - `pci_prd_multi_root_ok()`
  - `pci_prd_root_complex_iter()`
  - `pci_prd_slot_name()`
- Compatibility:
  - `pci_prd_compat_flags_t`
  - `PCI_PRD_COMPAT_NONE`
  - `PCI_PRD_COMPAT_ISA`
  - `PCI_PRD_COMPAT_PCI_NODE_NAME`
  - `PCI_PRD_COMPAT_SUBSYS`
  - `pci_prd_compat_flags()`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/memlist.h`, and `sys/sunddi.h`. The comments state that platform modules named `pci_prd` implement these functions and may depend on platform mechanisms such as ACPI.

## Research Notes
Interfaces are generally called from kernel context during boot, single-threaded by the caller. Resource discovery primarily fills gaps not visible through ordinary PCI scanning.
