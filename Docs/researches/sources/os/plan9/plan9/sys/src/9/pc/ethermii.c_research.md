# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethermii.c

Shared MII/PHY helper implementation used by multiple Ethernet drivers. It depends on a caller-provided `Mii` object with controller pointer and `mir`/`miw` callbacks for device-specific PHY register access.

`mii()` probes PHY addresses selected by a bitmask. For each unprobed address it reads `Bmsr`, then `Phyidr1`/`Phyidr2`, builds the OUI, ignores invalid all-ones/all-zero identifiers, allocates a `MiiPhy`, initializes advertisement/flow-control/master-slave cache fields to `~0`, installs it in `mii->phy[]`, selects the first PHY as `curphy`, and updates mask/count. It returns a mask of PHYs found or already known in this probe.

`miimir()` and `miimiw()` are safe wrappers around the current PHY read/write callbacks. They reject nil MII/controller/current-PHY state. `miireset()` sets `BmcrR` in the current PHY control register and delays briefly.

`miiane()` configures autonegotiation advertisement. It checks that the PHY supports autonegotiation, chooses 10/100 advertisement bits either from caller input, cached PHY state, or capabilities in `Bmsr`, handles pause/asymmetric pause advertisement, and when extended status is present configures 1000BASE-T half/full-duplex advertisement in `Mscr` from caller input, cached state, or `Esr`. It writes `Mscr` and `Anar`, then sets `BmcrAne|BmcrRan` if not in reset.

`miistatus()` checks autonegotiation completion and link status, reading `Bmsr` twice because link status is sticky. It determines 1000/100/10 speed and duplex from master-slave status plus the intersection of advertised and link-partner abilities. For full-duplex links it resolves receive/transmit pause behavior from local and partner pause bits. It updates `MiiPhy` fields `link`, `speed`, `fd`, `rfc`, and `tfc`.

Notable risks: the helper assumes autonegotiation for status; callers that force link modes need external handling. Allocation failures during probe simply skip a PHY. It stores per-PHY cached advertisement state but does not free `MiiPhy` objects.
