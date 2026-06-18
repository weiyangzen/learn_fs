# File Research: sources/os/plan9/9front/sys/src/9/pc/squidboy.c

## Role

Multiprocessor application-processor startup code for 32-bit x86 PC kernels.

## Main Interfaces

- `mpstartap(Apic *apic)` prepares and starts an AP through the universal startup algorithm.
- Static `squidboy(Apic *apic)` is the C entry point reached by the AP bootstrap code.

## Key Behavior

- Allocates AP page tables, clones the bootstrap processor page directory, and installs a private `Mach` mapping at `MACHADDR`.
- Creates and registers the AP `Mach` structure, page directory, and GDT storage.
- Writes the AP bootstrap handoff data: C entry address, page directory physical address, and APIC pointer.
- Sets the BIOS warm-reset vector, writes the NVRAM shutdown code, and sends INIT/SIPI through `lapicstartap()`.
- AP entry initializes machine state, MMU, CPU ID, clock, LAPIC, timers, floating-point state, and enters `schedinit()`.

## Dependencies And Assumptions

- Depends on AP bootstrap assembly layout at `APBOOTSTRAP+0x08`.
- Assumes the AP bootstrap physical address is in the low warm-reset segment expected by the code.
- Uses LAPIC/APIC support from `mp.h` and platform clock hooks.

## Research Notes

- This file is small but critical: it bridges low-memory AP bootstrap assembly into the normal kernel scheduler.
- Startup waits up to roughly 100 ms for `apic->online`, updating TSC sync data when TSC is the fast clock.
