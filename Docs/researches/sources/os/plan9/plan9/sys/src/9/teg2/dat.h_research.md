# File Research: sources/os/plan9/plan9/sys/src/9/teg2/dat.h

Core Tegra 2 kernel data-structure header: time constants, architecture structs, MMU state, Mach layout, cache abstractions, IRQ numbers, and SoC address table.

Key contents:
- Defines `HZ`, watchdog timeout, CPU frequency conversion macros, and console index.
- Declares architecture types including `Conf`, `FPsave`, `Mach`, `MMMU`, `PMMU`, `Memcache`, `Cacheimpl`, `Soc`, `Uart`, and `Ether`.
- Defines ARM/VFP process FP save state and FP state flags.
- Defines `Conf` and `Confmem` physical-memory accounting.
- Defines per-Mach fields used by assembly first, followed by scheduler, clock, fault, interrupt, profiling, probing, and FPU state.
- Provides fake `kmap`/`kunmap` macros using the direct mapping.
- Defines global `active` CPU state, cache-line-isolated word wrapper, cache capability bits, cache implementation vtable, DMA mode enum, IRQ numbers, and SoC controller address struct.

Role:
- This file is the C-side ABI for most Tegra 2 port files, including assembly-known `Mach` offsets and cache-operation indirection.
- It captures the GIC interrupt numbering scheme: private interrupts 0-31 and Tegra shared-controller banks starting at 32.

Notable constraints:
- `NCOLOR` is 1; this ARM port does not need MIPS-style VCE cache coloring.
- `KMap` is fake because pages are addressed through the direct map.
- `MAXSYSARG` is 5, matching the generic Plan 9 syscall ABI expectation for this port.
