# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cap.h

## Purpose
Defines helper APIs and macros for locating, reading, writing, and dumping conventional PCI capabilities and PCIe extended capabilities through a DDI config access handle.

## Main Interfaces
- Extended-capability marker:
  - `PCI_CAP_XCFG_FLAG_SHIFT`
  - `PCI_CAP_XCFG_FLAG`
  - `PCI_CAP_XCFG_SPC()`
- Capability ID masks:
  - `PCI_CAP_XID_MASK`
  - `PCI_CAP_ID_MASK`
- Locate functions:
  - `pci_xcap_locate()`
  - `pci_lcap_locate()`
  - `pci_htcap_locate()`
  - `PCI_CAP_LOCATE()`
- Config access sizes:
  - `pci_cap_config_size_t`
  - `PCI_CAP_CFGSZ_8`
  - `PCI_CAP_CFGSZ_16`
  - `PCI_CAP_CFGSZ_32`
- Access macros:
  - `PCI_CAP_GET8/16/32`
  - `PCI_CAP_PUT8/16/32`
  - `PCI_XCAP_GET8/16/32`
  - `PCI_XCAP_PUT8/16/32`
- Core APIs:
  - `pci_cap_probe()`
  - `pci_cap_get()`
  - `pci_cap_put()`
  - `pci_cap_read()`
- Invalid-read constants:
  - `PCI_CAP_EINVAL8`
  - `PCI_CAP_EINVAL16`
  - `PCI_CAP_EINVAL32`
- Debug macro:
  - `PCI_CAP_DBG`

## Dependencies And Relationships
Uses `ddi_acc_handle_t` from DDI headers supplied by includers. It builds on `pci.h` capability definitions and is used by PCI/PCIe nexus and drivers that need capability-safe access.

## Research Notes
Extended-capability access is encoded by ORing the capability ID with `PCI_CAP_XCFG_FLAG`; the same generic get/put path can then distinguish conventional and extended capability spaces.
