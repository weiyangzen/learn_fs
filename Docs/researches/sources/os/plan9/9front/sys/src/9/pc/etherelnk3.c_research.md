# File Research: sources/os/plan9/9front/sys/src/9/pc/etherelnk3.c

3Com EtherLink III / Fast EtherLink / Fast EtherLink XL driver, registered as `elnk3`, `3C509`, and `3C575`.

Primary role:
- Supports a broad family of 3Com ISA, EISA, PCI, CardBus, and PCMCIA adapters with multiple datapaths: PIO FIFO, older bus-master upload, and 3C90x descriptor-list upload/download.

Key structures:
- `Pd`: 3C90x upload/download packet descriptor with hardware fields, next pointer, and block pointer.
- `Ctlr`: controller state including port/PCI/IRQ, window lock, attached flag, busmaster mode, PIO receive buffer, FIFO TX state, upload/download descriptor rings, statistics, media/transceiver state, EEPROM command type, RX threshold/status variant, and optional CardBus function MMIO.

Discovery paths:
- `tcm59Xpci()` scans PCI vendor `0x10B7`, requires I/O BAR, allocates I/O, enables PCI, resets TX/RX, creates `Ctlr`, handles CardBus/eeprom command variants for IDs `0x5157` and `0x6056`, and enables bus mastering.
- `tcm5XXeisa()` checks EISA signature, walks EISA slots, matches 3Com IDs, enables adapters, resets, and records IRQ.
- `tcm509isa()` performs the 3Com ISA ID-port activation sequence, skips EISA-mode port `0x3F0`, activates adapters, and records resources.
- `tcm5XXpcmcia()` accepts PCMCIA types `3C589`, `3C562`, and `589E`.

Important behavior:
- `etherelnk3reset()` scans once, claims a controller, reads EEPROM device ID and MAC address, chooses busmaster mode and receive-status format, writes station address, selects media, initializes statistics/buffers/rings, sets thresholds, and installs callbacks.
- `attach()` programs RX filter, interrupt indication/enable masks based on busmaster mode, enables RX/TX, acknowledges CardBus interrupts, and primes upload/RX DMA if used.
- `transmit()` dispatches to FIFO `txstart()` or descriptor-list `txstart905()`.
- `txstart()` writes packet length and padded data to the FIFO when space exists; otherwise sets a TX-available threshold.
- `txstart905()` frees completed download descriptors, stalls/un-stalls the download engine when appending, links new packet descriptors, tracks queue depth, and starts the download list if idle.
- `receive()` handles FIFO/busmaster RX status, accounts errors, allocates replacement buffer, reads FIFO data or uses DMA completion pointer, discards hardware FIFO packet, queues good packet, and primes next DMA.
- `receive905()` consumes completed upload descriptors, accounts errors, replaces buffers, un-stalls upload, and tracks queue depth.
- `interrupt()` processes host errors, RX/transfer complete, upload complete, TX complete/error/underrun threshold adjustment, TX available, download complete, stats update, RX early, CardBus ACK, and panics on unhandled interrupt bits.
- `ifstat()` accumulates and prints hardware stats plus upload/download queue counters.

Media and PHY handling:
- `setxcvr()` programs old or new transceiver selection registers.
- `autoselect()` tries MII, then 100BaseTX link beat, then 10BaseT link beat, otherwise falls back to auto-select.
- `miir()` bit-bangs MII through window 4 physical management register.
- Reset logic handles media overrides via `media=...`, MII autonegotiation, full-duplex/force100 options, 100BaseTX/FX, 10BaseT, and 10Base2 DC converter setup.
- Specific newer devices force MII and call `resetctlr()` for CardBus/Tornado-like variants.

Research notes:
- The driver is complex because it spans several 3Com generations and bus types.
- CardBus adapters `0x5157`/`0x6056` need interrupt acknowledgment through mapped CardBus function space.
- Shutdown resets TX/RX through `resetctlr()`.
