# File Research: sources/os/plan9/9front/sys/src/9/pc/apic.c

Local APIC and I/O APIC support for the 9front PC kernel.

Key behavior:
- Defines local APIC register offsets, SVR/ICR/ESR/timer bits, divide table, and per-CPU APIC timer calibration state.
- `lapicinit` maps/initializes local APIC state, enables spurious vector, calibrates local APIC timer against `fastticks`, applies Pentium errata handling, masks local vectors, enables APIC error vector, and synchronizes arbitration IDs.
- `lapiconline` reloads the periodic timer and lowers APIC task priority for a CPU.
- `lapicstartap` sends INIT and STARTUP IPIs to boot an application processor.
- `lapicerror` and `lapicspurious` handle local APIC error/spurious interrupts.
- `lapicisr`, `lapiceoi`, and `lapicicrw` expose APIC ISR/EOI/ICR operations.
- `ioapicrdtr`, `ioapicrdtw`, and `ioapicinit` read/write redirection entries and mask all I/O APIC lines.
- `lapictimerset` programs one-shot timer deadlines; `lapicclock` calls MTRR synchronization and generic timer interrupt work.
- `lapicintron`, `lapicintroff`, `lapicnmienable`, and `lapicnmidisable` adjust APIC interrupt/NMI acceptance.

Research notes:
- Timer calibration increases APIC divide value if the measured rate is too high for the counter.
- The code includes compatibility handling for older Intel local APIC quirks.
