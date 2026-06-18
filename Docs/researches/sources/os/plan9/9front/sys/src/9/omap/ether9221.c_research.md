# File Research: sources/os/plan9/9front/sys/src/9/omap/ether9221.c

SMSC LAN9221 Ethernet driver for IGEPv2-style OMAP boards.

Key behavior:
- Defines LAN9221 register layout, FIFO command/status bits, interrupt bits, MAC/PHY indirect register access, EEPROM state, and multicast table storage.
- `smcreset` checks chip ID, resets hardware, waits for power readiness, configures FIFOs/MAC, loads or synthesizes Ethernet address, and initializes interrupt masks.
- `smcattach`, `smctransmit`, and `smcreceive` implement Plan 9 `Ether` driver operations using TX/RX FIFOs.
- `macrd`/`macwr` access MAC registers through the LAN9221 CSR synchronizer.
- `smcpromiscuous` toggles promiscuous receive mode.
- `smcmulticast` is present but effectively a stub.
- `smcinterrupt` acknowledges LAN9221 interrupts, handles RX/TX status, wakes receive/transmit paths, and clears GPIO IRQ state through `gpioirqclr`.
- Optional `USE_KPROCS` paths define RX/TX kernel processes but are disabled because comments report slower boot.
- `smcpnp` probes the board controller and installs driver hooks.
- `ether9221link` registers the driver as Ethernet type `9221`.

Research notes:
- The file documents board-specific assumptions: chip-select 5, base `0x2c000000`, GPIO pin 176/IRQ 34.
- The driver is FIFO-based rather than descriptor-ring based; comments note this is slow and DMA does not help much.
