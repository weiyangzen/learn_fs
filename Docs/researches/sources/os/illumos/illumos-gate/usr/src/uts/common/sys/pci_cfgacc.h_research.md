# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cfgacc.h

## Purpose
Defines a root-complex-relative PCI configuration-space access request format and typed get/put helpers for byte, word, dword, and qword accesses.

## Main Interfaces
- `PCI_GETBDF(b, d, f)`: encodes bus/device/function with special handling when device is zero.
- `pci_cfg_data_t`: union for 8/16/32/64-bit config values.
- `pci_config_size_t`: access sizes `PCI_CFG_SIZE_BYTE`, `WORD`, `DWORD`, `QWORD`.
- `pci_cfgacc_req_t`: request containing root-complex dip, BDF, offset, size, write flag, value, and `ioacc` flag.
- Value access macros:
  - `VAL8()`
  - `VAL16()`
  - `VAL32()`
  - `VAL64()`
- Config access functions:
  - `pci_cfgacc_get8/16/32/64()`
  - `pci_cfgacc_put8/16/32/64()`
  - `pci_cfgacc_acc()`

## Dependencies And Relationships
Includes `sys/dditypes.h` and is excluded for assembly. It provides low-level PCI config-space access plumbing for platform/nexus code.

## Research Notes
The request structure centralizes both read and write operations and carries the root-complex devinfo pointer, making it suitable for indirect configuration access paths.
