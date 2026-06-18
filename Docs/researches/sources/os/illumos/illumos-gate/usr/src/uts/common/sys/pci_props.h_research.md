# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_props.h

## Purpose
Defines shared PCI node-property construction data and helper functions used to unify boot-time and hotplug PCI node initialization.

## Main Interfaces
- `pci_prop_flags_t`:
  - `PCI_PROP_F_MULT_FUNC`
  - `PCI_PROP_F_PCIE`
  - `PCI_PROP_F_SLOT_VALID`
- `pci_prop_data_t`: captured device identity and classification data, including BDF, revision, header, class/subclass/programming interface, vendor/device/subsystem IDs, PCIe type, slot number, PCIe cap offset, interrupt pin, grant/latency, and status.
- `pci_prop_failure_t`:
  - `PCI_PROP_OK`
  - `PCI_PROP_E_BAD_READ`
  - `PCI_PROP_E_UNKNOWN_HEADER`
  - `PCI_PROP_E_BAD_PCIE_CAP`
  - `PCI_PROP_E_NDI`
  - `PCI_PROP_E_DDI`
- Property setup functions:
  - `pci_prop_data_fill()`
  - `pci_prop_name_node()`
  - `pci_prop_set_common_props()`
  - `pci_prop_set_compatible()`
- Shared class predicates:
  - `pci_prop_class_is_vga()`
  - `pci_prop_class_is_isa()`
  - `pci_prop_class_is_ioapic()`
  - `pci_prop_class_is_pcibridge()`

## Dependencies And Relationships
Includes fixed-width types and DDI types. Used by PCI enumeration paths that need consistent node naming and compatible-property creation.

## Research Notes
The failure enum preserves partial-read semantics: unknown headers and bad PCIe capabilities can still leave useful fields in `pci_prop_data_t`.
