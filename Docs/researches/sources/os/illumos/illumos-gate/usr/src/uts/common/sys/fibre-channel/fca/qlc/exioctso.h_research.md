# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioctso.h

This OS-dependent companion header supplies illumos/Solaris type aliases, platform limits, address-mode selection, and ioctl command numbers for the QLogic external ioctl ABI in `exioct.h`.

Key contents:
- Includes `sys/int_types.h`.
- Defines `INT8`, `INT16`, `INT32`, `INT64`, `UINT8`, `UINT16`, `UINT32`, and `UINT64`.
- Selects `EXT_ADDR_MODE_OS` as 64-bit under `LP64`, otherwise 32-bit.
- Defines OS limits for maximum HBAs, buses, targets, LUNs, non-SCSI3 LUNs, and AEN queue entries.
- Assigns OS ioctl command numbers from `EXT_CC_QUERY_OS` through `EXT_CC_GET_BBCR_DATA_OS`.
- Defines `EXT_CC_HBA_NODE_SBUS`.

Dependencies:
- Consumed directly by `exioct.h`.

Research notes:
- This file isolates OS-specific command-number and sizing decisions from the otherwise broad QLogic management ABI.
- Address mode selection is important for mixed 32-bit userland and 64-bit kernel ioctl handling.
