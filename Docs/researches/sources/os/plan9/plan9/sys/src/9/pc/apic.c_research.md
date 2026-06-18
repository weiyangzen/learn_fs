# File Research: sources/os/plan9/plan9/sys/src/9/pc/apic.c

Local APIC and I/O APIC support for PC SMP and timer interrupts.

Key responsibilities:
- Defines local APIC register offsets and bit masks.
- Provides `lapicr`/`lapicw` register access helpers.
- Initializes local APIC mode, spurious vector, error vector, LVT entries, timer, and arbitration synchronization in `lapicinit`.
- Calibrates local APIC timer against `fastticks` in `lapictimerinit`.
- Brings a CPU’s LAPIC online with periodic timer and lowered task priority.
- Starts application processors with INIT and STARTUP IPIs through `lapicstartap`.
- Handles APIC error/spurious interrupts and EOI.
- Provides IOAPIC redirection table read/write and initialization.
- Programs one-shot/periodic timer deadlines through `lapictimerset`.
- Bridges APIC clock interrupt to `timerintr`.
- Enables/disables LAPIC interrupt acceptance and NMI LVT.

Important behavior:
- APIC timer period is clamped between calibrated min/max.
- Some old Pentium steppings get an MSR workaround and suppress error reports.
- LAPIC timer reloads are staggered by CPU number to desynchronize processors.

Dependencies:
- Depends on MP/APIC structures from `mp.h`, x86 MSR helpers, `fastticks`, interrupt vectors, and generic timer/MTRR functions.

Notable risks:
- `lapictimerinit` panics if calibrated APIC clock appears faster than CPU clock outside tolerance.
- LAPIC access panics if `lapicbase` is not initialized.
