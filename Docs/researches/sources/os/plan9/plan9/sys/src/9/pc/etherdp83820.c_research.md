# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherdp83820.c

## Role

Plan 9 driver for National Semiconductor DP83820 10/100/1000 Ethernet controller. It registers as `DP83820`.

## Main Interfaces

- `etherdp83820link()` registers `dp83820pnp`.
- Ethernet callbacks: attach, transmit, interrupt, ifstat, promiscuous, multicast, shutdown.
- MII access is exposed through `dp83820miimir` and `dp83820miimiw`.

## Data Structures

- `Desc`: 64-bit-aligned TX/RX descriptor with link pointer, buffer pointer, command/status, extended status, and block pointer.
- `Ctlr`: MMIO state, EEPROM, config shadow, MII pointer, descriptor rings, global RX block pool use, MIB counters, and TX/RX error counters.

## Important Behavior

- Scans PCI Ethernet devices for DP83820 ID, maps BAR1 MMIO, and enables bus mastering.
- Resets controller, reads ATC93C46-style EEPROM, checks byte checksum, and derives MAC address from EEPROM words.
- Uses bit-banged MII management through `Mear`; attaches generic Plan 9 MII support unless TBI mode is enabled.
- Allocates RX/TX descriptor memory and a private receive block pool on first attach.
- RX descriptors are circular through hardware `link` fields; received good packets are queued and descriptors are replenished.
- TX path reclaims completed descriptors, counts descriptor error bits, queues packets, and restarts transmitter.
- Interrupt path handles RX, TX, MIB counter service, PHY changes, and TX underrun threshold adjustment.
- Receive filter accepts perfect-match, broadcast, and all multicast by default.

## Dependencies And Assumptions

- Depends on `ethermii.h` and Plan 9 PCI/MMIO/Ethernet APIs.
- File header states little-endian and 32-bit host assumptions.
- Uses global `dp83820rbpool` for receive block recycling.

## Notable Risks

- `dp83820ifstat()` assigns `edev` counters using `Mibd + offset` as an array index, which appears inconsistent with `ctlr->mibd[Nmibd]`.
- Promiscuous and multicast callbacks are effectively no-ops because filter defaults are broad.
- Reset contains disabled configuration code and prints diagnostic PCI/config values unconditionally.
- Several waits spin until reset/MII operations complete.
