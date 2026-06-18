# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci.h

## Purpose
Defines the public PCI configuration-space register map, class/subclass/programming-interface constants, capability identifiers and register layouts, BAR encodings, Open Firmware PCI address-property structures, and common PCI bus limits.

## Main Interfaces
- Standard configuration offsets:
  - `PCI_CONF_VENID` through `PCI_CONF_BIST`
  - Type 0 offsets for BARs, subsystem IDs, ROM, capabilities, and interrupts
  - Type 1 bridge offsets under `PCI_BCNF_*`
  - Type 2 CardBus offsets under `PCI_CBUS_*`
- Command/status/BIST/header bits:
  - `PCI_COMM_*`
  - `PCI_STAT_*`
  - `PCI_BIST_*`
  - `PCI_HEADER_*`
- PCI class, subclass, and programming interface constants for storage, network, display, multimedia, memory, bridges, communications, peripherals, input, docking, processors, serial bus, wireless, intelligent I/O, satellite, crypto, and signal-processing devices.
- BAR and ROM masks:
  - `PCI_BASE_*`
  - `PCI_BASE_ROM_*`
- Conventional capability list support:
  - `PCI_CAP_ID`
  - `PCI_CAP_NEXT_PTR`
  - `PCI_CAP_ID_*`
  - `PCI_CAP_NEXT_PTR_NULL`
- PM capability offsets and bits:
  - `PCI_PMCAP`
  - `PCI_PMCSR`
  - `PCI_PMDATA`
  - `PCI_PMCAP_*`
  - `PCI_PMCSR_*`
- PCI-X capability, bridge, ECC, command, and attribute definitions.
- SHPC/PCI hotplug register offsets and bit masks.
- MSI/MSI-X offsets, masks, vector-table layout constants, and maximum interrupt counts.
- Slot ID and HyperTransport capability constants.
- Property/address structures:
  - `pci_bus_range_t`
  - `pci_ranges_t`
  - `ppb_ranges_t`
  - `struct pci_phys_spec`
  - `pci_regspec_t`
- OF PCI address-cell masks/helpers:
  - `PCI_REG_*`
  - `PCI_ADDR_*`
  - `PCI_REG_*_G()`
  - `PCI_REG_MAKE_BDFR()`
- ROM data-structure constants and invalid-read constants:
  - `PCI_ROM_*`
  - `PCI_PDS_*`
  - `PCI_EINVAL8`, `PCI_EINVAL16`, `PCI_EINVAL32`, `PCI_EINVAL64`

## Dependencies And Relationships
Includes fixed-width and system types. It is the common public vocabulary used by PCI nexus drivers, device drivers, autoconfiguration, pcitool, PCIe code, and property construction.

## Research Notes
This header is pure ABI/register definition. PCIe-specific extended capability bodies are mostly in `pcie.h`, while this file retains the base PCI and conventional capability namespace.
