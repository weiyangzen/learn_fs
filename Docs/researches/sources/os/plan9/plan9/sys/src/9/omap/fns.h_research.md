# File Research: sources/os/plan9/plan9/sys/src/9/omap/fns.h

Declares OMAP machine-dependent functions, macros, and compatibility mappings used across the kernel.

Key points:
- Includes portable `portfns.h` and stubs `checkmmu()`/`countpagerefs()`.
- Declares cache, clock, CPU, coprocessor, DMA, MMU, UART, screen, watchdog, and trap/interrupt helpers.
- Maps Plan 9 `cycles(ip)` to `lcycles()`.
- Defines `intrenable()`/`intrdisable()` macros over OMAP `irqenable()`/`irqdisable()`, ignoring bus/TBDF.
- Declares FP emulation and FP process/syscall hooks.
- Declares uncached allocator and MMU map/unmap helpers.
- Provides Plan 9 machine macros: `CAS*`, `TAS`, `PTR2UINT`, `UINT2PTR`, `waserror()`, `KADDR()`, `PADDR()`, `wave()`, and `MASK()`.
- Declares global boot functions called from main: `archconfinit()`, `clockinit()`, `i8250console()`, `links()`, `mmuinit()`, `touser()`, and `trapinit()`.

Dependencies and interactions:
- Included by almost every OMAP C source file.
- Bridges portable kernel calls to OMAP-specific implementations.
- Coordinates assembly-provided routines and C implementations.

Research relevance:
- Central function declaration and macro adapter header for the OMAP port.
