# File Research: sources/os/plan9/9front/sys/src/9/pc/ether79c970.c

## Purpose
AMD PCnet PCI Ethernet driver for AMD79C970/79C970A/79C973-class devices, including VMware-emulated PCnet variants.

## Exposed Interface
- Link function: `ether79c970link()`
- Registers:
  - `addethercard("AMD79C970", reset)`

## Implementation Notes
- Uses receive and transmit descriptor rings:
  - RX ring: 64 descriptors.
  - TX ring: 16 descriptors.
- Supports both 16-bit and 32-bit I/O styles by probing RAP/RDP behavior after reset.
- `amd79c970pci()` finds PCI vendor/device `0x1022/0x2000`, reserves ports, and builds a controller list.
- `reset()` selects an inactive controller, enables PCI bus mastering, identifies chip version through CSR88/CSR89, reads station address from APROM unless overridden, and adjusts reported speed for VMware MAC OUIs.
- `ringinit()` allocates aligned descriptor rings and RX buffers, resets TX/RX indices, and prepares descriptors.
- Initializes the PCnet initialization block with ring lengths, MAC address, ring physical addresses, and points CSR1/CSR2 at it.
- Enables auto-padding in CSR4 and sets PCnet-PCI software style through BCR20.
- `interrupt()` acknowledges interrupts, records memory/missed/babble errors, processes RX descriptors into `etheriq()`, records RX/TX error counters, frees completed TX blocks, and restarts transmit.
- `promiscuous()` stops the chip, modifies CSR15, reinitializes rings, and restarts.
- `ifstat()` exports detailed RX/TX/chip error counters.

## Filesystem Relevance
Network driver only. It illustrates DMA descriptor-ring handling and Plan 9 generic Ethernet hooks (`attach`, `transmit`, `promiscuous`, `multicast`, `ifstat`).

## Risks / Quirks
- Header says “finish this rewrite”.
- Busy-waits on initialization completion.
- Promiscuous reconfiguration waits for all queued TX descriptors to drain.
- VMware-specific speed inference is based on MAC prefix, not negotiated link state.
