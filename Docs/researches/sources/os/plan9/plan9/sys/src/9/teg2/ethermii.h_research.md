# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.h

MII/PHY register, bit, and data-structure header for Ethernet drivers.

Key contents:
- Defines standard MII register numbers: BMCR, BMSR, PHY IDs, AN advertisement/link partner, expansion, next-page, 1000BASE-T control/status, and extended status.
- Defines BMCR control bits, BMSR capability/status bits, advertisement bits, 1000BASE-T master/slave bits, and extended status bits.
- Defines `Mii` containing discovered PHY table, current PHY, controller pointer, and driver read/write callbacks.
- Defines `MiiPhy` containing OUI, PHY number, advertised capabilities, flow control, 1000BASE-T control, link, speed, duplex, and flow-control results.
- Declares MII helper functions.

Role:
- Shared contract between generic `ethermii.c` and hardware drivers such as RTL8169.

Notable constraints:
- Supports up to 32 PHY addresses and 32 MII registers.
