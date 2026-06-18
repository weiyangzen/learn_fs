# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethermii.h

Header for the shared MII helpers. It declares `Mii` and `MiiPhy`, standard MII register numbers, register bit masks, structure layouts, and external helper prototypes.

The register enums cover basic mode control/status (`Bmcr`, `Bmsr`), PHY identifiers, autonegotiation advertisement/link-partner registers, next-page registers, 1000BASE-T master-slave control/status, and extended status. Bit enums define reset, loopback, speed select, duplex, autonegotiation enable/restart, power-down/isolate, link and capability bits, pause/asymmetric pause, remote fault, acknowledge/next page, 1000BASE-T half/full advertisement, partner 1000BASE-T support, and extended 1000BASE-X/T capability bits.

`Mii` embeds a `Lock`, tracks number and mask of detected PHYs, stores up to 32 `MiiPhy*` entries plus `curphy`, and carries opaque `ctlr` plus device-specific read/write callbacks. `MiiPhy` stores parent MII, OUI, PHY address, cached advertisement/flow-control/master-slave values, and current link/speed/duplex/flow-control result fields.

Exports are `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`. The header is hardware-neutral and is intended for NIC drivers to provide only low-level MII register access.
