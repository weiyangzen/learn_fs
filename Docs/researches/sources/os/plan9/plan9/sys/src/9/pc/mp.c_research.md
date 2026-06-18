# File Research: sources/os/plan9/plan9/sys/src/9/pc/mp.c

Intel MultiProcessor table parsing, APIC setup, SMP application-processor startup, interrupt routing, and MP shutdown/reset path.

Key elements:
- Parses MP configuration table entries into condensed `Bus`, `Apic`, and `Aintr` structures.
- `mkprocessor`, `mkbus`, `mkioapic`, `mkiointr`, `mklintr` build CPU, bus, I/O APIC, and interrupt route state.
- `mpintrinit` translates MP interrupt flags into APIC redirection-table bits.
- `checkmtrr` records and compares MTRR registers across CPUs.
- `squidboy` is the AP C entry point after trampoline startup; initializes Mach, MMU, CPU, LAPIC, timers, and scheduler.
- `mpstartap` builds AP page tables/Mach state, writes warm-reset vector and AP bootstrap parameters, then sends startup IPIs.
- `mpinit` initializes PIC/APIC, maps LAPIC, parses MP table, supplements CPU discovery with ACPI MADT, enables local APIC interrupts, starts APs, and sets `conf.copymode`.
- `mpintrenable` and `mpintrenablex` map Plan 9 interrupt controls to I/O APIC vectors and destinations.
- `mpshutdown` handles multiprocessor reboot/reset, including PCI reset, i8042 reset, and port `0xcf9` fallback.

Interactions:
- Uses structures and constants from `mp.h`.
- Calls `mpacpifunc` from `mpacpi.c` to discover CPUs missed by MP tables.
- Uses `vmap` for APIC MMIO, `intrenable` for local APIC vectors, and PCI helpers for PCI interrupt pins.

Research notes:
- ACPI support here is deliberately limited: MP tables remain the source for interrupt routing.
- Interrupt vector allocation uses unique APIC vectors to reduce lost-interrupt risk.
