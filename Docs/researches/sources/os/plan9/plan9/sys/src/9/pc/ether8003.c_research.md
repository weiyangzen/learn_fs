# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8003.c

Read completely: 273 lines.

This file implements Western Digital/SMC WD8003/8013/8216 Ethernet support using the shared DP8390 core.

Key behavior:
- Defaults to port `0x280`, IRQ `3`, memory `0xD0000`, and size `8 KB`.
- Validates card presence through LAN address ROM checksum.
- Distinguishes old 8003E-style boards, 8013EBT-style boards, 16-bit cards, and 8216 Elite Ultra cards.
- Determines IRQ, memory base, RAM size, and bus width from board registers.
- Enables shared memory and maps interface RAM.
- Configures DP8390 ring layout in shared memory.
- Copies MAC address from ROM unless overridden.
- Claims UMB memory with `umbrwmalloc()`.

Important interfaces:
- Link function: `ether8003link()`.
- Registered name: `WD8003`.
- Uses `ether8390.h` and DP8390 functions.

Research notes:
- `reset8003()` contains several hardware aliasing checks for older cards with limited register sets.
- `reset8216()` uses alternate registers to retrieve memory and IRQ.
- The DP8390 port is at `ether->port + 0x10`.
