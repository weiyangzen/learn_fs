# File Research: sources/os/plan9/9front/sys/src/9/pc/l.s

## Purpose
Provides 32-bit x86 bootstrap assembly, low-level CPU/port primitives, trap/syscall entry stubs, FPU/SSE helpers, synchronization helpers, VMX instruction wrappers, and the interrupt vector table.

## Key Elements
Bootstrap labels `_startKADDR`, `_multibootheader`, `_multibootentry`, `_startPADDR`, `mode32bit`, and `_startpg` handle multiboot metadata, early GDT setup, page-table construction, KZERO mapping, BSS clearing, Mach pointer setup, stack setup, and transfer to `main`. The file implements port I/O (`inb`, `outb`, string I/O), descriptor/control-register access (`lgdt`, `lidt`, `getcr*`, `putcr*`), TSC/MSR helpers, `cpuid`, `delayloop`, FPU/SSE save/restore, SPL interrupt priority functions, atomic/synchronization primitives, label save/restore, halt/mwait, RDRAND, debug-register helpers, VMX helpers, `touser`, common trap entry, syscall entry, `forkret`, and `vectortable`.

## Dependencies
Includes `mem.h` and shares constants with trap setup, segment descriptors, `Mach` layout assumptions, `main`, `trap`, `syscall`, and memory initialization (`MemMin` is written here and consumed by `memory.c`).

## Behavior/Risks
This file encodes hardware contracts directly: vector-table entry size is known by `trapinit()`, the first bootstrap page layout must match `mem.h`, and many instructions are emitted with raw bytes. Small layout or selector changes can break boot, trap return, user entry, or virtualization support.
