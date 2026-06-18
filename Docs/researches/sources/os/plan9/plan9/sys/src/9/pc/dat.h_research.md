# File Research: sources/os/plan9/plan9/sys/src/9/pc/dat.h

Core PC platform type definitions, process/MMU machine state, CPU feature flags, and architecture interface declarations.

Key contents:
- Forward declarations for BIOS32, configuration, PCMCIA, PCI, process/page/Mach, Ureg, and related types.
- Defines `Lock`, `Label`, x87/SSE FPU save structures, `FPsave`, `Confmem`, `Conf`, `PMMU`, and `Notsave`.
- Includes shared `../port/portdat.h`.
- Defines x86 `Tss`, GDT segment descriptor, and full `Mach` structure.
- Defines `KMap` aliases/macros and declares `kmap`/`kunmap`.
- Defines global `active` CPU/shutdown state.
- Defines `PCArch`, the architecture operations table for reset, power, interrupts, clocks, and peer CPU reset.
- Defines CPUID feature masks and parsed ISA configuration structure.
- Declares `arch`, `machp`, `m`, and `up`.

Role:
- The central machine-private ABI between PC assembly, MMU, traps, arch device, interrupt setup, process code, and port kernel code.

Important fields:
- `PMMU` stores page directory and page table-page lists per process.
- `Mach` contains per-CPU page directory/GDT/TSS, current process, performance counters, APIC timer lock, CPU ID/cache/TSC/MTRR state, and aligned FPU-save pointer.
- `PCArch` abstracts generic PC versus MP interrupt/clock implementations.

Notable risks:
- Many layouts are known to assembly or port code; structural changes require cross-file coordination.
- `up` is a macro through `MACHADDR`, not a normal global.
