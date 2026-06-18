# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_intr_lib.h

## Purpose
Declares PCI interrupt helper routines for MSI, MSI-X, INTx, class-to-PIL selection, and interrupt weighting.

## Main Interfaces
- `pci_class_val_t`: class-code/mask/value matching tuple.
- MSI/MSI-X helpers:
  - `pci_msi_get_cap()`
  - `pci_msi_configure()`
  - `pci_msi_unconfigure()`
  - `pci_is_msi_enabled()`
  - `pci_msi_enable_mode()`
  - `pci_msi_disable_mode()`
  - `pci_msi_set_mask()`
  - `pci_msi_clr_mask()`
  - `pci_msi_get_pending()`
  - `pci_msi_get_nintrs()`
  - `pci_msi_set_nintrs()`
  - `pci_msi_get_supported_type()`
  - `pci_msix_init()`
  - `pci_msix_fini()`
  - `pci_msix_dup()`
- INTx helpers:
  - `pci_intx_get_cap()`
  - `pci_intx_set_mask()`
  - `pci_intx_clr_mask()`
  - `pci_intx_get_pending()`
  - `pci_intx_get_ispec()`
- Interrupt policy helpers:
  - `pci_class_to_pil()`
  - `pci_class_to_intr_weight()`

## Dependencies And Relationships
Uses `dev_info_t`, DDI interrupt specs, and MSI-X state types from DDI headers. It is consumed by PCI/PCIe nexus drivers and interrupt allocation code.

## Research Notes
The API separates capability discovery, mode enable/disable, vector programming, masking, pending-state checks, and class-based interrupt prioritization.
