# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether2000.c

Read completely: 236 lines.

This file implements NE2000-compatible Ethernet support on top of the shared DP8390 driver.

Key behavior:
- Supports PCI NE2000-style adapters including Realtek 8029 and Winbond 89C940.
- Builds a controller list by scanning PCI Ethernet-class devices.
- Matches by known PCI IDs or an explicit `id=` option.
- Configures DP8390 parameters for NE2000 data/reset ports.
- Reads PROM through DP8390 remote DMA to validate marker bytes and obtain MAC address.
- Registers as `NE2000`.

Important interfaces:
- Link function: `ether2000link()`.
- Reset hook: `ne2000reset()`.
- Uses `etherif.h` and `ether8390.h`.
- Calls `dp8390reset()`, `dp8390read()`, and `dp8390setea()`.

Research notes:
- Defaults are `irq=2`, packet memory offset `0x4000`, and size `16 KB` when unspecified.
- `nodummyrr` option disables dummy remote reads.
- If PROM validation fails, the I/O range and allocated DP8390 state are released.
