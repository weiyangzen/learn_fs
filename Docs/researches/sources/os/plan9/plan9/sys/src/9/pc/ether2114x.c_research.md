# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether2114x.c

Read completely: 1836 lines.

This file implements Ethernet support for DEC Tulip 2114x-family PCI controllers and compatible PNIC/ADMtek variants.

Key behavior:
- Supports 21041, 21140, 21143, PNIC, PNIC-II, ADMtek Centaur-P, and CardBus ADMtek variants.
- Uses descriptor rings for receive and transmit.
- Reads and partially decodes serial ROM media information.
- Handles media selection through compact SROM blocks, MII PHY blocks, and fallback fake leaf data for non-conforming cards.
- Supports explicit medium and full-duplex options.
- Posts a Tulip setup packet to program the station address.
- Adapts transmit threshold after underflow.
- Reports extensive receive/transmit/error counters through `ifstat`.

Important interfaces:
- Link function: `ether2114xlink()`.
- Registered names: `2114x`, `21140`.
- Uses generic `Ether` hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `shutdown`, `multicast`, `promiscuous`.

Key internal pieces:
- `dec2114xpci()` scans PCI devices, maps I/O ports, resets controllers, and reads SROM.
- `srom()` reads EEPROM, locates station address, finds media info leaves, and probes PHYs.
- `media()`, `mediaxx()`, `media21041()`, `type0mode()`, `type2mode()`, `typephymode()`, and `typesymmode()` select and program media modes.
- `ctlrinit()` allocates rings, enables interrupts, starts transmit, and posts setup packet.
- `interrupt()` drains receive descriptors, reclaims transmit descriptors, tracks errors, and handles abnormal interrupts.

Research notes:
- Multicast is effectively always enabled via `Pm`; the multicast callback is a no-op.
- SROM decoding is partial and includes hard-coded leaves for known non-conforming cards.
- PNIC and ADMtek variants have special register handling.
