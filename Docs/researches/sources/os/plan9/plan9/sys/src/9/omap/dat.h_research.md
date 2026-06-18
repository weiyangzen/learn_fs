# File Research: sources/os/plan9/plan9/sys/src/9/omap/dat.h

Defines OMAP platform data types, kernel machine/proc MMU state, configuration structures, locks, FP save area, cache metadata, and DMA modes.

Key points:
- Defines time constants `HZ`, `MS2HZ`, `TK2SEC`, `Mhz`, and cycle-based `MS2TMR`/`US2TMR`.
- Documents that UART0/1 are ignored and OMAP UART3 is exposed as console 0.
- Declares platform typedefs for `Conf`, `Mach`, `Proc`, `Uart`, `Ureg`, `PTE`, `Tval`, `Memcache`, and more.
- Defines `Lock` with key, saved status register, PC, proc, mach, and ilock flag.
- Defines software-emulated `FPsave` with status/control and 8 internal FP register slots.
- Defines `Confmem`/`Conf` memory and kernel sizing fields.
- Defines `MMMU` and `PMMU` state: L1 table pointer/range, MMU PID, proc L2 page and L2 cache.
- Defines full `Mach` with scheduling, alarm, MMU, timing, interrupt/syscall/fault stats, performance, CPU frequency, exception save areas, and stack.
- Provides fake `kmap()`/`kunmap()` macros mapping pages through `kseg0`.
- Defines global active CPU state, `m` in R10, `up` in R9, `kseg0`, `machaddr`, `memsize`, and `normalprint`.
- Defines `ISAConf`, device-port/device-conf structures, `Memcache`, and DMA addressing modes (`Const`, `Postincr`, `Index`, `Index2`).

Dependencies and interactions:
- Included by most OMAP kernel files.
- Extends portable `portdat.h`.
- `fns.h`, MMU, clock, trap, UART, Ethernet, USB, and DMA code rely on these types.

Research relevance:
- OMAP port’s central machine data model and type contract.
