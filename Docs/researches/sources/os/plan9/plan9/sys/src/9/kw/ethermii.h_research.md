# File Research: sources/os/plan9/plan9/sys/src/9/kw/ethermii.h

## Purpose
Defines MII/PHY register numbers, bit masks, Marvell 88E1116-specific paged registers, and the `Mii`/`MiiPhy` structures used by generic and controller-specific Ethernet code.

## Key Contents
- Standard MII registers: `Bmcr`, `Bmsr`, PHY ID registers, autonegotiation advertisement/link partner registers, gigabit control/status, and extended status.
- Marvell-specific registers: `Scr`, `Ssr`, `Ier`, `Isr`, `Escr`, `Recr`, `Eadr`, `Globsts`, impedance registers, and `Scr2`.
- Basic control/status bits for reset, loopback, speed, duplex, power-down, autonegotiation, link status, capabilities, and extended status.
- Autonegotiation bits for 10/100 modes and pause/asymmetric pause.
- Gigabit capability/status bits for 1000BASE-T half/full duplex.
- Marvell page-specific bits for power-down, MDIX, energy detect, RGMII power-up, and TX/RX timing.
- `Mii`: controller pointer, PHY table, current PHY, probe mask, and MDIO callbacks.
- `MiiPhy`: OUI, address, advertised capability caches, link, speed, duplex, and flow-control state.
- Function prototypes for `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`.

## Dependencies and Integration
Included by `ethermii.c` and `ether1116.c`.

## Risks and Notes
The header mixes standard IEEE MII definitions with Marvell-specific extension registers, so users must select the correct register page before using page-specific constants.
