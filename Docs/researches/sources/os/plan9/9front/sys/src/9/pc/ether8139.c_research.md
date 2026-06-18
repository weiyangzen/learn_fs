# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8139.c

## Purpose
Realtek RTL8139 PCI Fast Ethernet driver, excluding RTL8129.

## Exposed Interface
- Link function: `ether8139link()`
- Registers:
  - `addethercard("rtl8139", rtl8139pnp)`

## Implementation Notes
- PCI probe supports Realtek 8139 and several compatible board IDs, plus user-specified `id=`.
- `rtl8139pnp()` builds an Ethernet-controller PCI list, matches a controller, fills `Ether` fields, reads station address if not overridden, installs hooks, and enables interrupts.
- `rtl8139attach()` lazily allocates RX buffer and four transmit buffers, then calls `rtl8139init()`.
- `rtl8139init()` resets/halt state, writes MAC address, initializes ring receive buffer, configures RX/TX DMA, interrupts, multicast hash registers, and enables TX/RX.
- RX model is the RTL8139 contiguous ring buffer:
  - `rtl8139receive()` tracks CAPR/CBR, handles wrap-around, copies packets to new `Block`s, strips CRC, and resets receiver on packet-status errors.
- TX model has four descriptors:
  - `rtl8139txstart()` queues blocks into descriptors, copying unaligned packets to aligned per-descriptor buffers.
  - `rtl8139interrupt()` frees completed descriptors, raises early-TX threshold on underrun, and restarts queueing.
- `rtl8139multicast()` computes Ethernet CRC hash and writes multicast filter registers.
- `rtl8139promiscuous()` toggles accept-all in RCR.
- `rtl8139stat()` reports configuration, counters, PHY/media registers, and alignment statistics.
- Link-change interrupt updates speed based on media status.

## Filesystem Relevance
Network driver only. It is useful for Plan 9 kernel networking and DMA ring-buffer patterns, not filesystem behavior directly.

## Risks / Quirks
- Receive errors trigger partial receiver reset and may need multicast state restoration per comment.
- PCIe variant multicast byte order branch is compiled out (`if (0 && ctlr->pcie)`).
- Static speed detection is minimal and mostly interrupt-driven thereafter.
