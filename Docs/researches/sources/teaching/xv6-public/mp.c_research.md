# File Research: sources/teaching/xv6-public/mp.c

Multiprocessor table discovery and CPU enumeration.

Key behavior:
- Searches BIOS areas for the MP floating pointer structure.
- Validates checksums and MP configuration table signatures/versions.
- Populates global `cpus[]`, `ncpu`, `ioapicid`, and `lapic`.
- Parses processor and I/O APIC entries; skips bus and interrupt-source records.
- Optionally masks external interrupts through IMCR on hardware that requires it.

Notable detail:
- Panics if no suitable MP table is found, reflecting xv6’s SMP-oriented assumptions.
