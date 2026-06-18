# File Research: sources/os/plan9/9front/sys/src/9/cycv/ethercycv.c

Cyclone V Ethernet MAC driver.

Key responsibilities:
- Registers Ethernet card type for Cyclone V.
- Manages descriptor rings and RX buffer replenishment.
- Implements RX and TX packet paths.
- Handles Ethernet interrupts and wakes worker paths.
- Initializes MAC/DMA hardware and PHY/MII.
- Implements attach, promiscuous mode, multicast hash filtering, and interface statistics.
- Parses or assigns Ethernet MAC address during probe.

Important behavior:
- RX buffers are aligned and DMA-cache managed.
- Multicast filtering uses hash computation over Ethernet addresses.
- Link and descriptor state are exposed through `ifstat`.

Dependencies:
- Plan 9 Ethernet/MII core, DMA/cache helpers, EMAC registers, interrupt controller, and platform reset/system manager registers.
