# File Research: sources/teaching/xv6-public/picirq.c

Legacy 8259A PIC disable support.

Behavior:
- Defines master and slave PIC I/O ports.
- `picinit` masks all interrupts on both controllers.

Role:
- xv6 relies on APIC/IOAPIC interrupt handling and disables the legacy PIC.
