# File Research: sources/os/plan9/9front/sys/src/9/cycv/io.h

Cyclone V physical I/O base addresses and IRQ constants.

Key contents:
- Defines UART, MPCore, L2 cache, clock manager, EMAC, reset manager, system manager, FPGA manager, OCRAM, DMA, and L3 base addresses.
- Defines reset-manager register offsets.
- Defines HPS clock value.
- Defines IRQ numbers for timer, UART0, EMAC1, FPGA manager, DMA channel 0, and DMA abort.
- Defines interrupt trigger constants `LEVEL` and `EDGE`.

Role:
- Shared hardware address/IRQ map for Cyclone V platform drivers.
