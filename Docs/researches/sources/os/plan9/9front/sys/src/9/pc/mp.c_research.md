# File Research: sources/os/plan9/9front/sys/src/9/pc/mp.c

Implements multiprocessor/APIC initialization support and interrupt assignment for the 32-bit PC kernel. Tables are populated by MP-table or ACPI discovery elsewhere; this file consumes the condensed bus/APIC structures from `mp.h`.

Key behavior:
- Global topology state: `mpbus`, `mpbuslast`, ISA/EISA bus numbers, `mpioapic[]`, and `mpapic[]`.
- `mpintrinit()` converts MP interrupt table flags into APIC redirection-vector bits, resolving default polarity/trigger mode from bus type.
- `syncclock()` synchronizes TSC state when the architecture fast clock uses `tscticks()`.
- `mpinit()` initializes legacy PIC fallback, LAPIC, local LAPIC interrupts, starts application processors through `mpstartap()`, and sets `conf.copymode` for SMP/old CPUs.
- `allocvector()` allocates APIC vectors spaced by priority class to reduce lost-interrupt risk.
- `mpintrassign()` first tries MSI, then table-driven I/O APIC routing, then local APIC vectors, then EISA/ISA fallbacks.
- MSI support includes HyperTransport MSI mapping enablement on AMD/NVIDIA platforms.
- `mpshutdown()` parks APs, broadcasts INIT, and resets PCI.

Research notes:
- Storage drivers in this group depend indirectly on this file through `intrenable()` routing for PCI interrupts and MSI/I/O APIC configuration.
- The interrupt assignment code handles PCI bridge swizzling when firmware tables omit downstream buses.
- The round-robin CPU selector uses online APICs and physical destination mode.
