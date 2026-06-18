# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arm.s

Shared ARMv6 assembly macro file.

Key contents:
- Includes `mem.h` and `arm.h`.
- Defines `PADDR(va)` and `L1X(va)` address/page-table helpers for assembly.
- Defines `PTEDRAM`, the cached/buffered section mapping attributes for DRAM.
- Defines `ISB`, `DSB`, and `BARRIERS` using CP15 cache/write-buffer operations.
- Defines an `MCRR` instruction emitter macro for cache-range operations.
- Defines `OKAY`, a GPIO write macro targeting BCM GPIO register `0x7E200028`.

Used by boot, exception, and reboot assembly.
