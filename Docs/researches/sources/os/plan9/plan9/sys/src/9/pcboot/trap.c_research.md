# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/trap.c

This file implements x86 trap and interrupt handling for the pc bootstrap kernel.

Key responsibilities:
- Maintains a `vctl[256]` dispatch table for traps and interrupts.
- `trapinit0` builds the IDT early enough to panic cleanly during initialization.
- `trapinit` installs handlers for breakpoint, page fault, double fault, and reserved trap 15, enables NMI, and exposes `irqalloc`.
- `intrenable` and `intrdisable` register and unregister interrupt handlers via architecture-specific hooks.
- `trap` dispatches interrupts, handles spurious interrupts, posts user notes for user exceptions, and panics on unhandled kernel traps.
- `fault386` handles page faults, including lazy `VMAP` synchronization and normal VM faults.
- Provides register dumps, stack dumps, kernel-process setup, fork-child register setup, and debugging PC helpers.
- `syscall` panics because bootstrap kernels do not implement system calls.

Filesystem/storage relevance:
- Page-fault handling is required for VMAP-backed device mappings used by storage/network drivers.
- Interrupt registration supports disk, network, and timer drivers during boot.
