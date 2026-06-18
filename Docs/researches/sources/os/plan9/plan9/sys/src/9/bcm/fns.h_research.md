# File Research: sources/os/plan9/plan9/sys/src/9/bcm/fns.h

BCM port function declaration header.

Key contents:
- Includes shared `../port/portfns.h`.
- Declares architecture/device helpers, cache/TLB/MMU functions, CP15 accessors, clock/timer functions, DMA functions, VideoCore mailbox helpers, framebuffer helpers, UART/screen/trap/process functions, FPU functions, and reboot/watchdog hooks.
- Defines Plan 9 portability macros for `intrenable`, `cycles`, `sdmalloc`, `sdfree`, `waserror`, `KADDR`, `PADDR`, `DMAADDR`, `DMAIO`, `getpgcolor`, and pointer/integer conversion.
- Declares floating-point emulation/VFP process hooks.
- Provides stubs/macros for unused or trivial platform operations such as `kmapinval()` and `countpagerefs()`.

This is the central C cross-module API for the BCM kernel port.
