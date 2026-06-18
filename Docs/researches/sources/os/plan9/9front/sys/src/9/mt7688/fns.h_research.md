# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fns.h

MT7688 MIPS platform function declarations and address macros. It exports clock, trap, MMU/TLB, kmap, interrupt, cache, FPU, bootargs, UART, low-level CP0/config, and architecture helper routines.

The header defines `KADDR`, `PADDR`, `KSEG1ADDR`, `FMASK`, user-reg detection, pointer/integer conversion helpers, and UART/serial console entry points. It also exposes MIPS-specific register accessors such as `rdcount`, `wrcompare`, `getcause`, `getstatus`, config reads, and watch register access.

Notable risks: several prototypes point to code outside this group; simple address macros assume the configured MIPS segment layout.
