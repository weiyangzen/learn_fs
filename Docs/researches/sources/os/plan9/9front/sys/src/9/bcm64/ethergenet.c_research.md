# File Research: sources/os/plan9/9front/sys/src/9/bcm64/ethergenet.c

Broadcom GENET Ethernet driver for BCM2711/Raspberry Pi 4.

Key responsibilities:
- Registers Ethernet card type `genet`.
- Maps GENET registers at `VIRTIO1+0x580000`.
- Manages RX/TX DMA descriptor rings and buffer pools.
- Runs kernel processes for receive, send, TX-free, and link-state monitoring.
- Handles GENET interrupt lines for DMA, MDIO, and link events.
- Implements MDIO read/write, MII setup, PHY reset/autonegotiation, and BCM PHY shadow-register tuning.
- Programs MAC address, multicast filters, promiscuous mode, and DMA/ring control.

Important behavior:
- Uses one main RX ring and one main TX ring with 256 descriptors each.
- RX replenishes buffers before handing completed packets to `etheriq()`.
- TX completion frees blocks asynchronously.
- `attach()` performs most hardware bring-up once and starts worker kprocs.
- MAC address comes from `getethermac()`.

Dependencies:
- Plan 9 Ethernet/MII core, DMA/cache helpers, interrupt controller, SoC address mapping, and mailbox MAC query.
