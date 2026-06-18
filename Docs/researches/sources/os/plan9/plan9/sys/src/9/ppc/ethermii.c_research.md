# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.c

## Role

Generic MII/PHY probing, reset, autonegotiation, and link-status helper for Ethernet drivers.

## Control Flow

`mii` scans PHY addresses from a mask, skips already-known PHYs, reads ID registers, filters invalid OUIs, allocates `MiiPhy`, initializes advertised capability caches, and selects the first PHY. `miimir` and `miimiw` call the current PHY read/write callbacks. `miireset` sets BMCR reset.

`miiane` checks autonegotiation support, chooses advertised 10/100 and optionally 1000Base-T capabilities from caller overrides, cached values, or PHY status registers, writes `Anar` and `Mscr`, then enables/restarts autonegotiation. `miistatus` reads status twice, determines link, speed, duplex, and pause-flow-control result from negotiated local/partner capabilities.

## Dependencies

Depends on `ethermii.h` register bits and driver-supplied `Mii.mir`/`Mii.miw`.

## Risks

Memory for discovered PHYs is never freed here. Status depends on cached advertisement fields being initialized through `miiane`. Return values are simple `-1/0`, so callers must decide how much degradation to tolerate.
