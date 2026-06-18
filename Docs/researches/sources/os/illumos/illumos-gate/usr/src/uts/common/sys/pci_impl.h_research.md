# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_impl.h

## Purpose
Defines private PCI implementation constants and helpers for x86 configuration mechanisms, PCI resource accounting, minor-number encoding, pcitool minor nodes, capability save sizing, and PCI resource setup/teardown.

## Main Interfaces
- x86 config mechanism constants:
  - `PCI_MECHANISM_UNKNOWN`
  - `PCI_MECHANISM_NONE`
  - `PCI_MECHANISM_1`
  - `PCI_MECHANISM_2`
  - `PCI_CONFADD`, `PCI_PMC`, `PCI_CONFDATA`, `PCI_CONE`
  - `PCI_CADDR1()`
  - `PCI_CSE_PORT`, `PCI_FORW_PORT`, `PCI_CADDR2()`
- `pci_acc_cfblk_t`: bus/device/function access block.
- `struct pci_bus_resource`: per-bus I/O, memory, prefetchable memory, and bus-number resource lists plus bridge/autoconfig metadata.
- Global/resource APIs:
  - `pci_bus_res`
  - `pci_memlist_alloc()`
  - `pci_memlist_free()`
  - `pci_memlist_free_all()`
  - `pci_memlist_insert()`
  - `pci_memlist_remove()`
  - `pci_memlist_find()`
  - `pci_memlist_find_with_startaddr()`
  - `pci_memlist_dump()`
  - `pci_memlist_subsume()`
  - `pci_memlist_merge()`
  - `pci_memlist_dup()`
  - `pci_memlist_count()`
- Minor-number macros:
  - `PCI_MINOR_NUM()`
  - `PCI_MINOR_NUM_TO_PCI_DEVNUM()`
  - `PCI_MINOR_NUM_TO_INSTANCE()`
  - `PCI_DEVCTL_MINOR`
  - `PCI_TOOL_REG_MINOR_NUM`
  - `PCI_TOOL_INTR_MINOR_NUM`
- Soft-state flags:
  - `PCI_SOFT_STATE_CLOSED`
  - `PCI_SOFT_STATE_OPEN`
  - `PCI_SOFT_STATE_OPEN_EXCL`
- Capability save-size constants:
  - `PCI_MSI_MIN_WORDS`
  - `PCI_PCIX_MIN_WORDS`
  - `PCI_PCIE_MIN_WORDS`
  - `PCI_PMCAP_NDWORDS`, `PCI_AGP_NDWORDS`, `PCI_SLOTID_NDWORDS`, `PCI_MSIX_NDWORDS`, HT capability sizes, and `PCI_CAP_SZUNKNOWN`
- Capability traversal macros:
  - `CAP_ID()`
  - `NEXT_CAP()`
- Resource lifecycle:
  - `pci_resource_setup()`
  - `pci_resource_destroy()`

## Dependencies And Relationships
Includes DDI types and memlist support. The x86-specific section is only compiled for `__i386` or `__amd64`.

## Research Notes
This is private nexus/autoconfig support, not a public PCI device-driver interface. It bridges hardware configuration access, resource list management, and driver minor-node conventions.
