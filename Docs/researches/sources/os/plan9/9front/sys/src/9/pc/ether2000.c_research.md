# File Research: sources/os/plan9/9front/sys/src/9/pc/ether2000.c

## Purpose
NE2000-compatible Ethernet driver glue for DP8390-based PCI/ISA adapters, including Realtek 8029 and Winbond 89C940 PCI variants.

## Exposed Interface
- Link function: `ether2000link()`
- Registers Ethernet card type:
  - `addethercard("ne2000", ne2000reset)`

## Implementation Notes
- Uses common DP8390 support from `ether8390.h`.
- PCI discovery builds a list of Ethernet-class PCI devices and matches known IDs or a user-specified `id=` option.
- `ne2000reset()` sets default IRQ/memory/size values, reserves I/O space, allocates a `Dp8390`, configures data port and ring offsets, resets the board through the NE2000 reset port, and probes PROM marker bytes.
- Reads the PROM through DP8390 remote DMA, validates marker bytes (`0x57` patterns, with a Parallels exception), and copies the station address unless already overridden.
- Calls `dp8390reset()` and `dp8390setea()` to initialize the shared 8390 core.

## Filesystem Relevance
This is a network device driver, not filesystem code. It is relevant to Plan 9 kernel device infrastructure and the generic `Ether` registration model that exposes network interfaces elsewhere in the OS.

## Risks / Quirks
- Old NE2000 assumptions: default IRQ 2, memory base `0x4000`, size 16 KiB.
- Supports unknown PCI IDs only through explicit `id=` option.
- Failed PROM validation frees resources and rejects the device.
