# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethersmc.c

SMC EtherEZ / SMC91cXX PCMCIA Ethernet driver. It registers `"smc91cXX"` and uses I/O ports plus PCMCIA tuple support rather than PCI discovery.

The file defines SMC91cXX banked registers, interrupt bits, MMU commands, receive/transmit status bits, packet header sizes, and an `Smc91xx` controller state with lock, revision, attach state, one pending TX block, TX allocation timestamp, and error/stat counters. `SELECT_BANK()` switches the chip register bank using the bank-select register.

`reset()` sets default IRQ/port if absent, reads an optional `id=` card type, opens a PCMCIA special slot, reserves I/O ports, allocates controller state, powers up and validates the chip ID, forces 16-bit mode, reads revision, reads the MAC address from the PCMCIA function-extension tuple if not already set, calls `chipreset()`, and installs generic `Ether` callbacks. On failure it releases I/O and PCMCIA resources.

`chipreset()` soft-resets RX/TX, writes the Ethernet address into bank 1 address registers, enables auto-release/error/counter interrupts, and resets the chip MMU. `chipenable()` enables normal TX/RX and masks in receive, receive-overrun, and EPH interrupts. `attach()` enables the chip once under the controller lock.

TX is MMU-allocation based. `txstart()` either resumes a saved block or dequeues a block, requests chip packet memory with `McAlloc`, handles `ArFailed` by enabling allocation interrupt and saving the block with timestamp, writes packet header and payload through the data port, enables TX error/empty interrupts, enqueues the packet, and frees the block. `transmit()` handles stalled saved allocations by resetting the chip after `TxTimeout`.

RX is FIFO based. `receive()` checks for RX FIFO empty, reads packet status and length from chip memory, updates generic Ethernet error counters on bad frames or allocation failure, otherwise copies payload into a new block, handles odd frame length, calls `etheriq()`, increments `inpackets`, and releases the packet from the MMU.

Interrupt handling saves/restores bank and pointer registers, masks interrupts while processing, loops over active masked causes, and dispatches receive, TX error, TX empty, allocation completion, RX overrun, and EPH events. `txerror()` reads TX status, updates lost-carrier/late-collision/16-collision counters, re-enables transmit, frees the failed packet, and restores packet selection. `eph_irq()` drains counter rollover state, re-enables TX after errors, and toggles control bits to clear link-error interrupts.

Promiscuous mode toggles `RcrPromisc`. Multicast handling does not hash addresses; it toggles all-multicast acceptance based on `ether->nmaddr`. `ifstat()` reports chip revision family and SMC-specific counters.

Notable risks: this is PCMCIA-only and depends on `pcmspecial` and CIS tuple data. The RX length expression relies on C operator precedence and appears intended to subtract header size from masked length. Multicast filtering is coarse all-multicast behavior.
