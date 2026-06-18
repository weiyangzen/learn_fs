# File Research: sources/os/plan9/plan9/sys/src/9/pc/x86watchdog.c

## Purpose
Implements a software-configured x86 watchdog using CPU performance counters and local APIC NMIs.

## Main Interfaces
- Exports `Watchdog x86watchdog`.
- Exports `x86wdstat(char*, char*)`.
- Exports `x86watchdoglink()` to register with `addwatchdog`.

## Implementation Notes
- Supports Intel P6, Intel P4, AMD K6/Athlon-family, and AMD64-family performance-counter models.
- `x86wdenable` wires the caller to CPU 0, checks CPUID vendor/family and required APIC/MSR/TSC features, resets relevant counters, enables local APIC NMI, and arms a roughly one-second counter overflow.
- `interval` caps the reload value at 31 bits for high-frequency CPUs.
- `x86wddisable` returns to CPU 0, disables local APIC NMI, and clears model-specific event selectors.
- `x86wdrestart` rewrites the counter reload and increments restart ticks.
- `x86wdstat` reports enabled/disabled plus restart count.

## Dependencies And Risks
- CPU 0 affinity is required because counters are local; `runoncpu` panics if it cannot switch.
- P4 handling has an early return if required MSR bit is absent, after `inuse` is already set.
- Low-level MSR programming is model-specific and assumes the APIC NMI path handles overflow correctly.
