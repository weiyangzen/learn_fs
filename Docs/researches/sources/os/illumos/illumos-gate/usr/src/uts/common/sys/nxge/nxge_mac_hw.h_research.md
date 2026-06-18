# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac_hw.h

## Purpose
Defines the MAC/PHY hardware ABI for NXGE: port type encoding, XMAC/BMAC/PCS/XPCS/ESR/MIF address calculations, register offsets, configuration/status masks, endian-aware register unions, counter masks, host-info entries, and SerDes/link diagnostic constants.

## Main Interfaces
- General port/PHY encoding:
  - `NXGE_PORT_SPD_*`
  - `NXGE_PHY_*`
  - `NXGE_PORT_1G_COPPER`
  - `NXGE_PORT_10G_FIBRE`
  - `NXGE_PORT_TN1010`
  - `nxge_network_mode_t`
  - `nxge_port_t`
  - `nxge_port_mode_t`
  - `nxge_linkchk_mode_t`
  - link interrupt/monitor enums
  - `xcvr_inuse_t`
- Address helpers:
  - `XMAC_REG_ADDR()`, `XMAC_PORT_ADDR()`
  - `BMAC_REG_ADDR()`, `BMAC_PORT_ADDR()`
  - `PCS_REG_ADDR()`, `PCS_PORT_ADDR()`
  - `XPCS_ADDR()`, `XPCS_PORT_ADDR()`
  - `ESR_ADDR()`
  - `MIF_ADDR()`
- BMAC register offsets and unions:
  - `btxmac_config_t`
  - `brxmac_config_t`
  - `bxif_config_t`
- XMAC register offsets and union:
  - `xmac_cfg_t`
- Register families for alternate addresses, hash tables, host-info tables, frame counters, byte counters, state machines, internal diagnostics, preamble data, and debug/training vectors.
- MIF definitions:
  - Clause 22/45 frame fields.
  - `mif_frame_t`
  - `mif_cfg_t`
  - `mif_poll_stat_t`
  - `mif_poll_mask_t`
  - `mif_stat_t`
- PCS definitions:
  - MII control/status/advertisement masks.
  - `pcs_ctrl_t`
  - `pcs_stat_t`
  - `pcs_anar_t`
  - `pcs_cfg_t`
  - `pcs_stat_mc_t`
- XPCS definitions:
  - Control/status/speed/package/test/config/mask/counter masks.
  - `xpcs_ctrl1_t`
  - `xpcs_stat1_t`
  - `xpcs_speed_ab_t`
  - `xpcs_dev_in_pkg_t`
  - `xpcs_ctrl2_t`
  - `xpcs_stat2_t`
  - `xpcs_stat_t`
  - `xpcs_test_ctl_t`
  - `xpcs_diag_t`
  - `xpcs_config_t`
- ESR/SerDes constants for reset, PLL, control, test config, RGMII config, signal observation, and loopback.
- Generic bit helpers:
  - `NXGE_BASE()`
  - `NXGE_VAL_GET()`
  - `NXGE_VAL_SET()`

## Dependencies And Relationships
Includes `nxge_defs.h` for base block addresses and shared helper constants. `nxge_mac.h` builds software stats/state on these register definitions, and MAC/PHY implementation code uses the address helpers and bit masks for link setup, reset, counters, filtering, and diagnostics.

## Research Notes
This is the largest MAC ABI header in the group and is highly sensitive to endian and bitfield ordering. It preserves support for both 10G XMAC and 1G BMAC paths, plus internal PCS/XPCS and external MII/MDIO access through MIF.
