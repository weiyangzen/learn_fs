# File Research: sources/os/plan9/plan9/sys/src/9/pc/l.s

- Size/hash: 1319 lines, 30391 bytes, SHA-256 `f677daa0a6bc72aca517f2cfa337b336aad91ed1938b94c45ef8e959987eb816`.
- Purpose: Core x86 assembly support for Plan 9 PC kernel startup, real-mode BIOS transitions, port I/O, control registers, CPU feature probes, floating point, spl/atomics, halt, and trap vectors.
- Boot path: `_startKADDR` jumps to physical `_startPADDR`; `_multibootheader` provides multiboot metadata; `_startPADDR` installs an initial GDT, enters 32-bit mode, builds bootstrap page tables, enables paging, clears BSS, initializes `m`, creates a stack, clears EFLAGS, and calls `main`.
- Initial memory setup: Uses `CPU0PDB`, `CPU0PTE`, `CPU0PTE1`, `CPU0GDT`, `CPU0MACH`, `MACHADDR`, and page-table macros from `mem.h`.
- Low-power path: `idle` loops with `STI; HLT`; `halt` conditionally halts only when `nrdy` indicates no ready process.
- Real-mode support: `realmode0`, `physcode`, `again16bit`, `now16real`, and return paths switch between paged protected mode and real mode to execute BIOS interrupts with register state stored in the real-mode Ureg area.
- BIOS32 support: `bios32call` loads register arguments, performs a far call through a supplied pointer, stores results, and returns carry status.
- Port I/O: Implements `inb/insb/ins/inss/inl/insl` and `outb/outsb/outs/outss/outl/outsl`.
- CPU registers/features: Implements `lgdt`, `lidt`, `ltr`, CR0/CR2/CR3/CR4 accessors, `invlpg`, `wbinvd`, `_cycles`, `lcycles`, `rdmsr`, `wrmsr`, `cpuid`, and `aamloop`.
- Floating point: Provides x87 and SSE enable/disable/save/restore/status/env/clear routines: `fpon`, `fpoff`, `fpinit`, `fpx87save`, `fpx87restore`, `fpstatus`, `fpenv`, `fpclear`, `fpssesave0`, `fpsserestore0`.
- Interrupt priority/atomic helpers: Defines `splhi`, `spllo`, `splx`, `islo`, `tas`, `_xinc`, `_xdec`, memory barriers, `xchgw`, `cmpswap486`, `mul64fract`, `gotolabel`, and `setlabel`.
- Trap path: `_strayintr` and `_strayintrx` build `Ureg` frames and call `trap`; `forkret` restores state; `vectortable` defines 256 vector stubs with syscall vector `0x40` routed to `_syscallintr`.
- Dependencies: Includes `mem.h` and `/sys/src/boot/pc/x16.h`; depends on C symbols including `main`, `trap`, `m`, `nrdy`, and kernel memory constants.
- Research notes: Foundational architecture code. It has broad indirect filesystem impact because it establishes the kernel execution environment, interrupt handling, TLB behavior, and syscall entry used by all OS services.
