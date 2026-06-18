# File Research: sources/os/plan9/9front/sys/src/9/ppc/etherfcc.c

Ethernet driver for MPC8260 FCC controllers.

Key responsibilities:
- Defines FCC Ethernet parameter RAM layout, descriptor-ring sizes, event bits, mode bits, and controller state.
- Attaches/closes by enabling/disabling FCC receive/transmit and scheduling link polling.
- Configures promiscuous mode based on explicit promisc and multicast state.
- Transmits by draining Ethernet output queue into cached buffer descriptors, flushing cache lines, and handing descriptors to the FCC.
- Handles RX/TX interrupts, receive descriptor recycling, error accounting, TX completion, TX restart on selected errors, and statistics histograms under debug.
- Initializes FCC ports, clocks, parameter RAM, descriptor rings, receive buffers, interrupt masks, and CPM commands following the MPC8260 guide sequence.
- Integrates MII management through bit-banged MDIO/MDC and periodic link/duplex polling.
- Registers as `addethercard("fcc", reset)`.

Dependencies:
- Uses `imm`/`m8260` register definitions, CPM operations, Plan 9 Ethernet queues, MII helpers, cache maintenance, timers, and interrupt registration.

Notable behavior:
- Buffer descriptors are allocated in normal memory, not dual-port RAM, due to documented cache/DMA hang behavior on some MPC8260 silicon.
- Requires an Ethernet address from configuration; reset fails if it remains all zero.
