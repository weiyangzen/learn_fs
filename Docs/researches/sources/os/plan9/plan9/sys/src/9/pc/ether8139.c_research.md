# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8139.c

Read completely: 879 lines.

This file implements Ethernet support for Realtek RTL8139 PCI devices and compatible cards.

Key behavior:
- Supports Realtek RTL8139 plus SMC and D-Link PCI IDs.
- Maintains one large receive ring buffer and four transmit descriptors.
- Handles PCI power-management wake-up and restores BAR/interrupt/cache-line config.
- Initializes MAC address, receive configuration, multicast hash registers, transmit buffers, and interrupts.
- Receives packets by walking the NIC circular receive buffer and copying into Plan 9 `Block`s.
- Transmits directly from aligned blocks or copies unaligned packets into descriptor staging buffers.
- Handles link-speed changes and adjusts output queue limits for 10/100 Mbps.
- Provides `ifstat` output for registers, counters, multicast, alignment, and error state.

Important interfaces:
- Link function: `ether8139link()`.
- Registered name: `rtl8139`.
- Generic Ethernet hooks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, `shutdown`.

Research notes:
- Receive configuration accepts broadcast, multicast, and physical-match packets.
- Multicast hash uses Ethernet CRC high bits.
- PCIe multicast byte ordering code exists but is disabled by `if (0 && ctlr->pcie)`.
- Serious system errors trigger reinitialization.
