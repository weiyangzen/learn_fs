# File Research: sources/os/plan9/plan9/sys/src/9/kw/ethermii.c

## Purpose
Provides generic MII/PHY probing, reset, autonegotiation, register access wrappers, and link-status decoding for Ethernet drivers.

## Main Functions
- `mii`: probes PHY addresses in a mask, reads ID registers, allocates `MiiPhy` entries, records OUI/PHY number, sets default advertised capability caches, and picks `curphy`.
- `miimir` and `miimiw`: access current PHY registers via driver-supplied MDIO callbacks.
- `miireset`: sets the PHY reset bit and spins until reset clears.
- `miiane`: configures autonegotiation advertisement for 10/100, pause, asymmetric pause, and optionally 1000BASE-T capabilities, then enables/restarts autonegotiation.
- `miistatus`: verifies autonegotiation/link status, determines negotiated speed and duplex from 1000BASE-T status or ANAR/ANLPAR overlap, and derives receive/transmit flow-control direction.

## Dependencies and Integration
Requires driver-supplied `Mii.mir` and `Mii.miw` callbacks, register definitions from `ethermii.h`, and memory allocation.

## Risks and Notes
Status reads follow the common sticky-link-status pattern by reading `Bmsr` twice. `miireset` busy-waits without timeout, so a stuck PHY reset bit can hang the caller.
