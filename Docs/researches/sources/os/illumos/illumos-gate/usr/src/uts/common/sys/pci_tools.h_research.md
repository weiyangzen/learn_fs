# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_tools.h

## Purpose
Defines the kernel/user ioctl ABI for PCI diagnostic tools that read/write device or nexus registers and inspect or modify interrupt-to-CPU mappings.

## Main Interfaces
- Versioning:
  - `PCITOOL_V1`
  - `PCITOOL_V2`
  - `PCITOOL_VERSION`
- Minor-node suffixes:
  - `PCI_MINOR_REG`
  - `PCI_MINOR_INTR`
- Ioctls:
  - `PCITOOL_DEVICE_GET_REG`
  - `PCITOOL_DEVICE_SET_REG`
  - `PCITOOL_NEXUS_GET_REG`
  - `PCITOOL_NEXUS_SET_REG`
  - `PCITOOL_DEVICE_GET_INTR`
  - `PCITOOL_DEVICE_SET_INTR`
  - `PCITOOL_SYSTEM_INTR_INFO`
- BAR selectors:
  - `PCITOOL_CONFIG`
  - `PCITOOL_BAR0` through `PCITOOL_BAR5`
  - `PCITOOL_ROM`
  - `PCITOOL_BASE`
  - `pcitool_bars_t`
- `pcitool_errno_t`: pcitool-specific status values such as invalid CPU, invalid interrupt, alignment/range errors, ROM disabled/write, I/O error, invalid size, unknown header, and invalid register offset.
- Interrupt payloads:
  - `pcitool_intr_set_t`
  - `pcitool_intr_dev_t`
  - `pcitool_intr_get_t`
  - `PCITOOL_IGET_SIZE()`
  - `pcitool_intr_info_t`
- Interrupt flags and controller types:
  - `PCITOOL_INTR_FLAG_SET_GROUP`
  - `PCITOOL_INTR_FLAG_GET_MSI`
  - `PCITOOL_INTR_FLAG_SET_MSI`
  - `PCITOOL_CTLR_TYPE_*`
- Register access attributes:
  - `PCITOOL_ACC_ATTR_SIZE_*`
  - `PCITOOL_ACC_ATTR_SIZE()`
  - `PCITOOL_ACC_ATTR_ENDN_*`
  - `PCITOOL_ACC_IS_BIG_ENDIAN()`
- `pcitool_reg_t`: register read/write request/result payload.

## Dependencies And Relationships
Includes `sys/modctl.h` for driver-name sizing and relies on `MAXPATHLEN` from common system headers. It is the ABI used by pcitool-style userland utilities and PCI nexus drivers.

## Research Notes
The structures carry both userland and driver ABI versions. Register requests explicitly include access width, endianness, logical target, returned physical address, and status.
