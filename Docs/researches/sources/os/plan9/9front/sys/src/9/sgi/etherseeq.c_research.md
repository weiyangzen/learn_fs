# File Research: sources/os/plan9/9front/sys/src/9/sgi/etherseeq.c

Implements a SEEQ 8003 Ethernet driver attached through SGI HPC3 DMA. It registers an `ether` card type named `seeq`.

The driver models HPC3 Ethernet registers with `Hio`, uses descriptor rings for RX/TX, and runs separate receive and transmit kernel processes. RX descriptors are replenished with page-sized buffers, packets are copied to allocated Blocks and queued with `etheriq`; TX descriptors are filled from `edev->oq` and kicked through HPC3 DMA state.

`startup` initializes DMA fixes, rings, station address, receive mode, and status registers. `shutdown` resets the channel. Interrupts clear overflow/completion and wake the RX/TX paths. Promiscuous and multicast are no-ops because the driver always receives promiscuously.
