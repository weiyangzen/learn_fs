# File Research: sources/os/plan9/9front/sys/src/9/pc64/squidboy.c

Multiprocessor AP startup coordinator for the PC64 kernel.

Key behavior:
- `squidboy` is the C entry point called by AP bootstrap assembly. It initializes the AP’s `Mach`, MMU, CPU identity, optional architecture clock, clock synchronization, APIC state, timers, and then enters the scheduler.
- `mpstartap` allocates AP page tables, a GDT page, and a `Mach` structure.
- Builds AP mappings by sharing the kernel high-half and VMAP mappings from CPU 0, plus a low double-map needed by the bootstrap transition.
- Fills the fixed AP bootstrap data slots at `APBOOTSTRAP+0x08` with the C entry vector, PML4 physical address, APIC pointer, `Mach` pointer, and NX/EFER bit.
- Programs the warm-reset vector and CMOS shutdown code, sends the LAPIC startup sequence, waits for the AP to mark itself online, then clears the shutdown code.

Notable dependencies:
- AP bootstrap code in `apbootstrap.s`.
- LAPIC/MP structures and APIC startup helpers.
- `mmuwalk`, `xspanalloc`, and CPU0 page tables.

Research notes:
- The AP shares top-level kernel/VMAP mappings but owns its PML4, low bootstrap mapping, GDT, and `Mach`.
- The code assumes `APBOOTSTRAP` remains in the first 64KB-compatible range; it prints a diagnostic if the warm-reset segment is not zero.
