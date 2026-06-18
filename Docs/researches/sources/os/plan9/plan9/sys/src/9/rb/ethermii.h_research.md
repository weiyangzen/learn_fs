# File Research: sources/os/plan9/plan9/sys/src/9/rb/ethermii.h

MII/PHY register and structure definitions.

Key contents:
- Defines standard MII register numbers: BMCR, BMSR, PHY IDs, autonegotiation, gigabit control/status, and extended status.
- Defines bit masks for BMCR, BMSR, ANAR/ANLPAR, MSCR, MSSR, and ESR.
- Defines `Mii` with PHY table, current PHY, controller pointer, and MDIO callbacks.
- Defines `MiiPhy` with OUI, address, advertisement state, link/speed/duplex, and flow-control flags.
- Declares MII helper functions.

Role:
- Shared API for Ethernet drivers that need generic PHY probing and autonegotiation.

Notable risks:
- Covers common standard registers only; vendor-specific PHY setup must live elsewhere.
