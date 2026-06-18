# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fns.h

This header declares `5e` emulator functions.

Covered interfaces:
- Allocation: `emalloc`, `emallocz`, `erealloc`.
- Process and executable loading: `initproc`, `loadtext`, `cleanup`, process list management.
- Memory/segment management: `newseg`, `vaddr`, `vaddrnol`, `freesegs`, `segunlock`, `copyifnec`, `bufifnec`, `copyback`.
- CPU execution: `step`, `syscall`, `clrex`.
- Error/note handling: `cherrstr`, `noteerr`, `suicide`, `donote`, `addnote`, `dump`.
- Fd table: `newfd`, `copyfd`, `fddecref`, `iscexec`, `setcexec`, `fdclear`.
- Procfs service: `initfs`.
- Floating point: FPA and VFP reset, transfer, and operation functions.
- Stack top-of-stack initialization: `inittos`.

Dependencies and interactions:
- Complements `dat.h`; all implementation files include both.

Research relevance:
- Public internal API map for the emulator.

Risk notes:
- Function signatures encode emulated 32-bit ARM addresses as `u32int`; host pointers must not leak into emulated state except through explicit copies.
