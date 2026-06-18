# File Research: sources/os/plan9/9front/sys/src/9/pc/ether2114x.c

## Purpose
DEC 2114x/Tulip-family PCI Fast Ethernet driver covering Digital 21041/21140/21143, Lite-On PNIC/PNIC-II, and ADMtek Centaur variants.

## Exposed Interface
- Link function: `ether2114xlink()`
- Registers Ethernet card types:
  - `addethercard("2114x", reset)`
  - `addethercard("21140", reset)`

## Implementation Notes
- Implements descriptor-ring transmit/receive with 64 RX descriptors and 64 TX descriptors.
- `dec2114xpci()` scans PCI Ethernet devices, filters supported IDs, reserves I/O ports, exits 21143 sleep mode when needed, resets hardware, decodes SROM, and builds a controller list.
- `srom()` reads serial ROM, identifies MAC address layout, fabricates SROM leaves for PNIC/ADMtek, parses media info blocks, tracks selected connection type, and scans MII PHYs for type 1/3 blocks.
- Media handling is the core complexity:
  - `media21041()` handles 21041 media programming.
  - `mediaxx()` dispatches compact/extended SROM media blocks.
  - `type0mode()`, `type2mode()`, `typesymmode()`, `typephymode()`, and `typephylink()` program CSR6/CSR12-15 or MII PHYs for selected media.
  - User options can force half/full duplex or a named medium from `mediatable`.
- `ctlrinit()` allocates RX/TX rings, initializes descriptors, enables interrupts, starts transmit state, builds a setup packet for the station address, and opens the output queue.
- `interrupt()` handles normal/abnormal interrupts, receives packets, records RX/TX errors, frees transmitted buffers, tops up TX, and raises TX threshold after underflow.
- `txstart()` sends either pending setup packet or queued data blocks and kicks the NIC.
- `ifstat()` exports counters and an SROM dump.
- `promiscuous()` toggles CSR6 promiscuous mode; multicast is always accepted via `Pm`.

## Filesystem Relevance
Network driver only, but useful for kernel substrate research: it shows PCI enumeration, EEPROM parsing, media negotiation, DMA ring ownership, and Plan 9 `Ether` integration.

## Risks / Quirks
- Comments list incomplete work: thresholds, ring sizing, fuller error handling, setup packet cleanup, attach-time initialization, and full SROM decoding.
- Some media paths contain guessed or special-case programming for old hardware.
- `interrupt()` panics on unhandled status bits.
- Shutdown prints and performs a software reset.
