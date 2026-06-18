# File Research: sources/teaching/xv6-public/main.c

Kernel C bootstrap and AP startup coordination.

Key behavior:
- `main` initializes allocator phase 1, kernel VM, MP tables, APICs, segmentation, PIC disable, IOAPIC, console/UART, process table, traps, buffer/file tables, IDE, other CPUs, allocator phase 2, first user process, then enters scheduler.
- `mpenter` is the AP C entry after `entryother.S`.
- `mpmain` loads IDT, marks CPU started, and calls `scheduler`.
- `startothers` copies AP startup code to `0x7000`, allocates AP stacks, patches entry parameters, sends startup IPIs, and waits for each AP to report started.
- Defines `entrypgdir`, the initial two-entry 4 MiB page directory mapping low memory both identity and at `KERNBASE`.

Important interactions:
- Filesystem initialization (`iinit`, `initlog`) is deferred to `forkret` in process context.
