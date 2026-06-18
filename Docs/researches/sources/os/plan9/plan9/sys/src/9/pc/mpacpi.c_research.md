# File Research: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.c

Minimal ACPI support for multiprocessor CPU discovery through RSDT/XSDT and MADT/APIC tables.

Key elements:
- Searches for `RSD PTR ` using `sigsearch`.
- Validates ACPI checksums for RSDP, RSDT/XSDT, and child tables.
- `mpacpiscan` maps ACPI descriptor tables with `vmap`, iterates table pointers, and dispatches valid tables.
- `mpacpitbl` handles `APIC` tables only.
- `mpacpicpus` walks MADT structures and processes local processor APIC entries.
- `mpacpiproc` enables usable local APIC processor records, maps the bootstrap LAPIC, records `bootapic`, and enables LAPIC through MSR `0x1b` if needed.
- `mpnewproc` and `apicset` populate shared `mpapic`/`machno2apicno` data.

Interactions:
- Hooks into `mp.c` through exported `void (*mpacpifunc)(void) = mpacpi`.
- Uses `mpacpi.h` table structs and `mp.h` APIC structures.

Research notes:
- Explicitly avoids AML; it discovers processors but does not derive interrupt routing.
- It can add CPUs not present in the legacy MP table, but does not replace MP routing logic.
