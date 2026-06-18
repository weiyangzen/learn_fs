# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/l.s

## Purpose
386 Plan 9 low-level assembly source defining bootstrap, paging setup, processor register helpers, interrupt entry stubs, floating-point state routines, and small runtime primitives.

## Key Areas
- Memory and machine constants: page size, kernel/user address bases, segment selectors, descriptor flags, PTE bits, and interrupt flag.
- `origin`, `lowcore`, and `mode32bit` bootstrap code:
  - optional real-mode relocation for boot builds,
  - GDT setup,
  - switch to protected mode,
  - BSS clearing,
  - temporary page-table construction,
  - paging enable,
  - jump into `KZERO`.
- Global data symbols: `mach0`, `u`, `m`, `tpt`, `tgdt`, `tgdtptr`.
- I/O primitives: `inb`, `outb`, `inss`, `outss`.
- Register/control helpers: `putidt`, `putgdt`, `putcr3`, `puttr`, `getcr0`, `getcr2`.
- Floating-point routines: `fpoff`, `fpinit`, `fpsave`, `fprestore`, `fpstatus`.
- Interrupt/trap stubs: `intr0` through selected vectors, `intrbad`, shared `intrcommon`/`intrscommon`.
- Scheduler/control primitives: `spllo`, `splhi`, `splx`, `idle`, `gotolabel`, `setlabel`, `touser`, `config`.

## Research Notes
Although located in the `8a` area in this work item, this is kernel-facing assembly using the syntax accepted by `8a`.
