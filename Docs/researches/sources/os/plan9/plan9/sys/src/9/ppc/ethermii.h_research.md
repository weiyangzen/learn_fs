# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethermii.h

## Role

Defines MII register numbers, bit masks, and data structures for generic PHY management.

## Main Definitions

Includes BMCR/BMSR, PHY ID, autonegotiation, master/slave 1000Base-T, and extended-status registers. Bit masks cover reset, loopback, power-down, autonegotiation, 10/100/1000 capabilities, pause/asymmetric pause, and link partner status.

`Mii` stores PHY count, mask, per-address `MiiPhy` pointers, current PHY, controller pointer, and read/write callbacks. `MiiPhy` stores OUI, address, cached advertisement/flow-control/master-slave settings, status, link, speed, duplex, and flow-control result.

## Interfaces

Declares `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`.

## Risks

The header abstracts register access only; drivers must supply correct bus timing and serialization. Constants assume standard IEEE MII register layout.
