# File Research: sources/teaching/xv6-public/mp.h

Definitions for Intel MultiProcessor Specification tables.

Contents:
- `struct mp` floating pointer structure.
- `struct mpconf` configuration table header.
- `struct mpproc` processor table entry and `MPBOOT`.
- `struct mpioapic` I/O APIC table entry.
- MP table entry type constants.

Used by `mp.c` during CPU and APIC discovery.
