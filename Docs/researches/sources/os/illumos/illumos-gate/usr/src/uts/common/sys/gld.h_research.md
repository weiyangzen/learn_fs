# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gld.h

## Role

`gld.h` is the public driver-facing interface for the legacy Generic LAN Driver framework. It defines GLD statistics, the `gld_mac_info_t` registration block, media/link/capability constants, exported GLD driver functions, and VLAN tag helpers.

## Key Interfaces and Data

- `media_stats_t` contains media-specific MIB-II counters for Ethernet, token ring, and FDDI.
- Compatibility macros alias media counters into `gld_stats`.
- `struct gld_stats` holds multicast/broadcast counters, errors, collisions, buffer drops, interrupts, 64-bit packet/byte counters, speed, duplex, media, unknown protocols, media-specific stats, and bad-interpreter counters.
- `gld_lock_t` preserves old ABI layout while allowing an rwlock implementation.
- `gld_mac_info_t` is the driver registration structure. Fields marked "SET BY DRIVER" include devinfo, vendor and broadcast addresses, interrupt cookie, margin, max/min packet sizes, identity string, media type, address and SAP length, PPA, capabilities, driver private callbacks, and send/tagged send hooks. Many reserved fields preserve binary layout.
- Promiscuous constants describe no-op, none, physical, and multicast modes.
- Capabilities include link-state notification, IP/TCP/UDP checksum offload variants, and zerocopy.
- Link-state values are down, unknown, and up.
- Media type constants include AUI, BNC, twisted pair, fiber, 10/100 variants, token ring, PHY MII, and InfiniBand.
- Return values include success, no resources, unsupported, bad argument, no link, retry, and failure.
- Kernel exports include allocation, registration, receive, tagged receive, link-state, scheduling, interrupt, STREAMS open/close/wput/wsrv/rsrv, and getinfo routines.
- VLAN macros construct and deconstruct TCI/VTAG fields, masks, priorities, CFI, VID, and TPID.

## Dependencies and Use

The file includes `sys/ethernet.h` and is used by GLD network drivers. `gldpriv.h` contains the framework-private structures layered behind this public registration ABI.

## Research Notes

The structure layout is intentionally ABI-sensitive, with explicit original statistic sizes and reserved padding. Driver code must only touch fields documented as driver-owned.
