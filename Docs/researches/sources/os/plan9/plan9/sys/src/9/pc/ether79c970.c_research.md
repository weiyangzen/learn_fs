# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether79c970.c

Read completely: 660 lines.

This file implements Ethernet support for AMD PCnet PCI controllers.

Key behavior:
- Supports AMD 79C970, 79C970A, and 79C973-style PCnet variants.
- Probes PCI vendor/device `0x1022/0x2000`.
- Supports either 16-bit or 32-bit I/O access by probing register behavior.
- Allocates receive and transmit descriptor rings aligned to 16 bytes.
- Builds a PCnet initialization block with MAC address and ring addresses.
- Handles receive and transmit interrupts with descriptor ownership bits.
- Supports promiscuous mode by stopping the chip, changing CSR15, reinitializing rings, and restarting.
- Treats multicast as promiscuous.

Important interfaces:
- Link function: `ether79c970link()`.
- Registered name: `AMD79C970`.
- Generic Ethernet hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, `shutdown`.

Research notes:
- Receive buffers are `ETHERMAXTU + 4` to include CRC.
- Transmit uses queued blocks directly in descriptors.
- Initialization enables the device immediately because VMware’s simulated 79C970 did not restart correctly after an older stop sequence.
