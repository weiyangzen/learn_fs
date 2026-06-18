# File Research: sources/os/plan9/plan9/sys/src/9/rb/ethermii.c

Generic MII/PHY helper implementation for Ethernet drivers.

Key responsibilities:
- Probes PHY addresses in a mask, reads PHY IDs, allocates `MiiPhy`, and selects a current PHY.
- Provides current-PHY register read/write wrappers.
- Resets a PHY through BMCR reset.
- Programs auto-negotiation advertisement for 10/100, pause, and optional 1000BASE-T modes.
- Determines link status, speed, duplex, and flow-control from BMSR, ANLPAR, MSCR/MSSR, and advertised capabilities.

Important behavior:
- Reads BMSR twice in `miistatus` because link status is sticky.
- Stores user/driver advertisement preferences in `MiiPhy`.
- Handles 1000BASE-T before falling back to 10/100 negotiation.

Dependencies:
- Requires driver-supplied `mir` and `miw` MDIO operations.

Notable risks:
- Returns `-1` for incomplete autonegotiation or link down; callers must tolerate transient failures.
- No freeing path for allocated `MiiPhy` objects.
