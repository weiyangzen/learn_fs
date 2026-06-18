# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc.h

## Purpose
Defines the EEPROM/SPROM content layout used by NXGE to discover factory MAC addresses, port counts, module strings, board model strings, PHY type, firmware/image size, interrupt counts, version, and checksum.

## Main Interfaces
- ESPC NCR register aliases such as `ESPC_MAC_ADDR_0`, `ESPC_NUM_PORTS_MACS`, module string registers, board model string registers, `ESPC_PHY_TYPE`, `ESPC_MAX_FM_SZ`, `ESPC_INTR_NUM`, `ESPC_VER_IMGSZ`, and `ESPC_CHKSUM`.
- Masks and shifts for packed SPROM fields, including port count, MAC address count, string lengths, firmware image size, version, and checksum.
- String access macros `ESPC_MOD_STR(n)` and `ESPC_BD_MOD_STR(n)`.
- PHY encoding constants `ESC_PHY_10G_FIBER`, `ESC_PHY_10G_COPPER`, `ESC_PHY_1G_FIBER`, `ESC_PHY_1G_COPPER`, and `ESC_PHY_NONE`.
- Bitfield unions:
  - `mac_addr_0_t`
  - `mac_addr_1_t`
  - `phy_type_t`
  - `intr_num_t`

## Dependencies And Relationships
Includes `nxge_espc_hw.h` for register address construction. The parsed values are consumed by ESPC/SPROM routines declared in `nxge_impl.h`, especially MAC address and PHY discovery during attach.

## Research Notes
The unions expose both 64-bit raw values and endian-aware byte/field access. This file is a hardware-data layout contract, not an algorithmic component.
