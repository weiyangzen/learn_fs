# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mac.h

## Purpose
Defines software MAC-layer state and statistics for NXGE XMAC/BMAC ports, including MTU limits, interrupt masks, link state, transceiver capabilities, counters, multicast hash filters, address tables, and host-info state.

## Main Interfaces
- MTU/frame constants:
  - `NXGE_MTU_DEFAULT_MAX`
  - `NXGE_DEFAULT_MTU`
  - `NXGE_MIN_MAC_FRAMESIZE`
  - `NXGE_MAXIMUM_MTU`
- MAC interrupt-mask composites for XMAC and BMAC TX/RX.
- `nxge_link_state_t`
- Common stats:
  - `nxge_mac_stats_t`
- Per-MAC counters:
  - `nxge_xmac_stats_t`
  - `nxge_bmac_stats_t`
- `hash_filter_t`: multicast hash refcounts and per-bit refcounts.
- `nxge_mac_t`: port identity/mode, link check mode, jumbo flag, config registers, frame sizing, pause/control state, MAC/alternate/filter addresses, hash table, host-info entries, stats pointers, and default MTU.

## Dependencies And Relationships
Includes `nxge_mac_hw.h` and `npi_mac.h`. The state is initialized and manipulated by MAC/PHY routines declared in `nxge_impl.h`.

## Research Notes
The header abstracts over XMAC and BMAC while keeping separate counter structures because the two hardware blocks expose different counter widths and semantics.
