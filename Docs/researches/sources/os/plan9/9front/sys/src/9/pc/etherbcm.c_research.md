# File Research: sources/os/plan9/9front/sys/src/9/pc/etherbcm.c

Broadcom BCM57xx Gigabit Ethernet driver, registered as `bcm`.

Primary role:
- Drives many Broadcom NetXtreme-class BCM57xx PCI/PCIe adapters using MMIO, send/receive rings, status block, MII PHY access, and interrupt mailbox handling.

Key structures:
- `Ctlr`: transmit/interrupt locks, linked-list pointer, MMIO base, PCI device, mapped register/status/ring pointers, receive-return and receive-producer indices, send indices, send/receive block arrays, active flag, duplex flag, and PHY number.

Supported devices:
- Large Broadcom device-ID table includes BCM5700/5701/5702/5703/5704/5705/5706/5708/5709, BCM5714/5715/5716/5717/5718/5719/5720/5721/572x, BCM575x/576x/577xx/578x/5906 and related IDs.

Important behavior:
- `bcmpci()` scans PCI network devices from vendor `0x14e4`, maps BAR0 MMIO, allocates descriptor/status memory, send/receive block arrays, determines PHY number, and builds a controller list.
- `bcmpnp()` claims an inactive controller, enables PCI/bus mastering, installs callbacks, initializes the chip, and enables interrupts.
- `bcminit()` performs a detailed hardware initialization sequence: PCI/MAC/arbiter setup, firmware handshake via memory window magic, DMA/coalescing engines, RCBs, receive producer/return rings, send ring, status block, MAC address read, PHY reset, link check, hash/filter setup, MSI mode, and interrupt unmasking.
- `replenish()` allocates receive blocks and posts producer descriptors.
- `bcmreceive()` consumes receive-return descriptors, validates block index, drops errored frames, and queues packets.
- `bcmtransmit()` fills send descriptors from `oq`, stores owning blocks, and advances the send host index.
- `bcmtransclean()` frees sent blocks according to status producer index.
- `bcminterrupt()` masks/acknowledges via interrupt mailbox, reads status block, handles errors/link changes/RX/TX cleanup, transmits more, and re-enables via tag write.
- `checklink()` uses MII registers to determine link, speed, duplex, updates Plan 9 link/speed state, and adjusts MAC port mode.

Error handling:
- `bcmerror()` panics on selected fatal flow-attention or RISC halted states, clears MAC event status, and logs DMA errors.
- Top comment explicitly says proper fatal error handling, multiple rings, QoS, and checksum offload are not implemented.

Research notes:
- Multicast callback is a no-op; initialization sets MAC hash registers to all ones, effectively accepting hashed multicast broadly.
- The source contains several hardware-magic constants and comments indicating empirical initialization requirements.
- No `ifstat` or shutdown callback is installed.
