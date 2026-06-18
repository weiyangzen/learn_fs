# File Research: sources/os/plan9/9front/sys/src/9/zynq/etherzynq.c

Purpose: Zynq GEM Ethernet driver for 9front’s `etherif` layer.

Key behavior:
- Defines GEM, PHY, DMA descriptor, and SLCR clock constants.
- MDIO read/write helpers wait for PHY idle.
- `ethproc` monitors link, configures 10/100/1000 speed, duplex, and GEM clock divisors.
- RX ring replenishes `Block`s, handles DMA descriptor ownership, invalidates caches, and queues packets.
- TX path pulls from output queue, cleans caches, fills descriptors, and starts transmit.
- Interrupt handler processes management completion, TX, RX, RX-used, and overrun events.
- Supports promiscuous mode and multicast hash programming.
- `etherpnp` creates a single controller with default MAC and registers it.

Integration notes: Uses Plan 9 network interface APIs, `vmap`, `xspanalloc`, `ucalloc`, cache maintenance, and Zynq SLCR clock registers.

Risk/attention points: Static default MAC is hardcoded. Descriptor/cache ordering depends on explicit `coherence()` and cache maintenance.
