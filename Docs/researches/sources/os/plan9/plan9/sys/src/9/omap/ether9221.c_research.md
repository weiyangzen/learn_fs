# File Research: sources/os/plan9/plan9/sys/src/9/omap/ether9221.c

Implements the SMSC LAN9221 Ethernet driver for IGEPv2-style OMAP boards.

Key points:
- Targets SMSC 9221 at `0x2c000000`, chip select 5, IRQ 34 via GPIO pin 176/module 6.
- Defines full register layout for FIFO ports, status, IRQ, FIFO info, power, MAC CSR, EEPROM, and related control registers.
- Uses FIFO-based RX/TX, with comments noting it is slow and DMA was not beneficial here.
- `macrd()`/`macwr()` perform indirect MAC CSR access through `maccsrcmd`/`maccsrdata`.
- `smcifstat()` reports driver counters and stored EEPROM words.
- `smcpromiscuous()` toggles MAC promiscuous mode; multicast callback accepts all multicast.
- `smctxstart()` checks TX FIFO space, ensures word alignment, writes TX command words and packet data into TX FIFO, and enables TX interrupts.
- `smctransmit()` drains the generic Ethernet output queue into the chip FIFO, putting back a block if FIFO is full.
- `smcattach()` lazily marks the controller initialized, optionally starts kprocs if enabled, installs polling fallback if no IRQ, and announces no DMA.
- `smcreceive()` drains RX status/data FIFOs into Plan 9 blocks, validates lengths/errors, and passes packets to `etheriq()`.
- `smcinterrupt()` clears the GPIO IRQ, reads interrupt status, handles RX/TX interrupt causes, drains TX status FIFO, and either wakes kprocs or directly receives/transmits.
- `smcdetach()` disables interrupts, clears pending status, flushes RX/TX FIFOs, and disables IRQ output.
- `smcreset()` powers up, verifies chip ID and byte test register, writes MAC address registers, enables TX/RX, configures FIFO/IRQ/MAC control, and enables RX/TX interrupts.
- `smcpci()` probes the memory-mapped device and builds a controller list; despite the name, this is platform memory-mapped discovery.
- `smcpnp()` binds a free controller to generic `Ether`, sets IRQ/port/speed, and installs attach/transmit/interrupt/ifstat/promiscuous/multicast/shutdown callbacks.
- `ether9221link()` registers card type `"9221"` with the generic Ethernet layer.

Dependencies and interactions:
- Registered through `addethercard()` in `devether.c`.
- Platform declaration comes from `archether()` in `archomap.c`.
- GPIO interrupt acknowledge is provided by `gpioirqclr()` in `archomap.c`.
- Uses generic `etheriq()` and output queues from `devether.c`.

Research relevance:
- Board-specific Ethernet hardware driver for the OMAP port, bridging SMSC9221 FIFOs to Plan 9 netif.
