# File Research: sources/os/plan9/plan9/sys/src/9/pc/mp.h

Definitions for Intel MultiProcessor Specification tables and APIC state used by `mp.c`, APIC code, and ACPI MP supplement code.

Key elements:
- Defines raw MP floating pointer `_MP_`, configuration header `PCMP`, processor/bus/I/O APIC/interrupt entries, and extended MP entry structs.
- Enumerates MP table entry types, CPU/I/O APIC enable flags, interrupt polarity/trigger flags, interrupt delivery types, and bus address-space metadata.
- Defines condensed runtime `Bus`, `Aintr`, and `Apic` structures.
- Defines APIC register numbers and redirection/vector bits such as `ApicFIXED`, `ApicNMI`, `ApicLOW`, `ApicLEVEL`, `ApicIMASK`.
- Declares I/O APIC, LAPIC, MP init, interrupt-enable, and shutdown entry points.
- Exposes global `_mp_`.

Interactions:
- Included by `mp.c` and `mpacpi.c`.
- Runtime `Apic` state is shared between MP-table and ACPI-discovered CPUs.

Research notes:
- This is hardware topology metadata, not filesystem code.
- `MaxAPICNO` is 254; APIC ID 255 is reserved for physical broadcast.
