# File Research: sources/teaching/xv6-public/ioapic.c

Implements I/O APIC initialization and IRQ routing.

Key behavior:
- Maps IOAPIC MMIO registers at physical `0xFEC00000`.
- Provides indexed register read/write helpers.
- `ioapicinit` checks IOAPIC ID against MP-discovered `ioapicid`, then disables all redirection entries.
- `ioapicenable` enables an IRQ and routes it to a target APIC ID/CPU.

Role:
- Replaces legacy PIC interrupt routing in xv6’s SMP setup.
