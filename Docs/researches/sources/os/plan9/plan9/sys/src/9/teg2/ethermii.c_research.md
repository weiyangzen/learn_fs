# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.c

Generic MII/PHY support for Ethernet drivers.

Key responsibilities:
- Probes PHY addresses using driver-supplied `mir`/`miw` operations and records discovered PHYs.
- Provides current-PHY read/write helpers `miimir` and `miimiw`.
- Resets the current PHY through BMCR reset.
- Configures auto-negotiation advertisements for 10/100, pause, and 1000BASE-T capabilities in `miiane`.
- Reads link/autonegotiation status in `miistatus`, deriving speed, duplex, receive flow control, transmit flow control, and link state.

Important behavior:
- Reads `Bmsr` twice because link status is sticky.
- 1000BASE-T status is checked before resolving 10/100 advertised common modes.
- Flow-control resolution follows advertised pause/asymmetric pause combinations only for full duplex.

Dependencies and assumptions:
- Depends on `ethermii.h` register definitions and a controller-populated `Mii` with valid callbacks.
- Allocates `MiiPhy` records dynamically as PHYs are discovered.

Notable risks:
- `miireset` does not wait for reset completion beyond a one-microsecond delay.
- If allocation fails during probe, that PHY is silently skipped.
