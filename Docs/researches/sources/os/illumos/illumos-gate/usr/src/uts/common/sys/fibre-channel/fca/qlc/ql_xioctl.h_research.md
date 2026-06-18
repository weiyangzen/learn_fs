# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_xioctl.h

## Role

`ql_xioctl.h` defines extended ioctl support structures and helper interfaces for the `qlc` Fibre Channel adapter driver. It bridges management utilities to mailbox, flash, VPD, firmware image, LED, link-statistics, AEN, and fabric management operations.

## Major Definitions

The file includes:
- Management server loop IDs for older and 24xx adapters.
- `ql_mbx_ret_t`, a mailbox return-register container.
- Name-match flags for node name, port name, port ID, and loop ID.
- CT information unit preamble layout and directory-server type.
- Big-endian link statistics counters.
- REPORT LUN header/list structures.
- Flash chip information and flash description table structures.
- Flash manufacturer IDs, device IDs, and flash type flags.
- LED/beacon state flags for older and 24xx adapters.
- PCI option ROM header/data structures and code-type constants.
- Firmware cache entry `ql_fcache_t` and firmware image type flags.
- Flash layout table pointer/header/region structures.
- Function/port configuration map structures, with function types for NIC, FC, iSCSI, and vNIC.
- Flash region identifiers for firmware, boot code, VPD, NVRAM, flash description, error logs, golden firmware, bootloader, and 8021-specific regions.
- `ql_xioctl_t`, the per-adapter extended ioctl context containing flash description, adapter I/O statistics, SNIA counters, AEN tracking queue state, and flags.

## Interfaces

The prototypes include resource allocation/free for xioctl state, the `ql_xioctl` dispatcher, AEN enqueueing, firmware-cache setup/release/search, LED blinking, FCode/PCI dump and load helpers, and loop-point configuration.

## Integration Notes

This header is coupled to external FC HBA ioctl definitions via `<exioct.h>` and to QLogic driver state through `ql_adapter_state_t`. It also duplicates some flash-description concepts found in hardware headers because ioctl utilities need stable payload definitions for firmware and flash operations.
