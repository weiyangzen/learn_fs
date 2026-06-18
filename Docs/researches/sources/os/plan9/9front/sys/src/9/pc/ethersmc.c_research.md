# File Research: sources/os/plan9/9front/sys/src/9/pc/ethersmc.c

Implements PCMCIA SMC EtherEZ / SMC91cXX Ethernet support.

Key behavior:
- Defines banked SMC91cXX I/O registers, transmit/receive control bits, MMU commands, FIFO ports, interrupt flags, status bits, and statistic counters.
- Uses PCMCIA tuple `FUNCE` node-id data to read the Ethernet address when not supplied.
- Resets the chip, programs the MAC address, enables auto-release and error/counter interrupts, resets the chip MMU, and enables RX/TX on attach.
- TX path allocates chip packet memory pages through the SMC MMU, writes packet header/data through PIO, handles allocation failure by saving the block and enabling allocation interrupt, then enqueues for transmit.
- RX path reads current RX packet through the chip FIFO, checks status/error bits, allocates a Plan 9 block, handles odd-frame padding, and submits to `etheriq`.
- Interrupt handler saves/restores bank and pointer registers, masks interrupts while servicing RX, TX error, TX empty, allocation completion, RX overrun, and EPH events.
- Tracks link/carrier/collision/defer/overrun counters and exposes chip revision/statistics via `ifstat`.
- Supports promiscuous mode and all-multicast mode based on `ether->nmaddr`.

Dependencies:
- Uses Plan 9 PCMCIA helpers, I/O port allocation, Ethernet/block APIs, and interrupt registration.
- Relies on 16-bit PIO access and SMC91cXX internal MMU/FIFO semantics.

Research notes:
- This is a non-PCI DMA driver; packet movement is programmed I/O through banked registers.
- TX timeout recovery resets/re-enables the chip if a saved transmit block cannot be allocated for too long.
- Multicast filtering is coarse: it toggles all-multicast rather than maintaining a hash table.
