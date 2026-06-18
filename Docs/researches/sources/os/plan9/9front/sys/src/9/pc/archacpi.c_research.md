# File Research: sources/os/plan9/9front/sys/src/9/pc/archacpi.c

ACPI-based PC architecture discovery, interrupt routing, AML I/O glue, and reset support.

Key responsibilities:
- Finds and maps ACPI RSDT/XSDT/FADT/DSDT/SSDT/MADT/HPET tables with checksum validation and memory reservation.
- Converts MADT processor, local APIC, I/O APIC, and interrupt-source override entries into the MP/APIC structures used by the rest of the PC kernel.
- Loads DSDT/SSDT AML, calls `_PIC`, discovers embedded controllers, and walks `_PRT` methods to add PCI interrupt routes.
- Provides `#P/acpitbls` for raw mapped table reads and `#P/acpimem` for restricted physical memory access.
- Implements ACPI reset through the FADT reset register when available, then falls back to generic reset.
- Supplies AML address-space handlers for system memory, I/O ports, PCI config space, and embedded-controller space.

Important behavior:
- `maptable()` recursively follows RSDT/XSDT and FADT pointers while de-duplicating physical table addresses.
- `memcheck()` blocks reads/writes that overlap low CPU bootstrap memory, the running kernel image, or configured usable RAM.
- PCI `_PRT` routes can use direct GSIs or link devices via `_PRS`, `_CRS`, and `_SRS`.
- Adds identity-mapped legacy ISA interrupts after ACPI routing.
- Can use HPET or TSC as the architecture fast clock depending on tables and boot options.

Dependencies:
- Depends on the AML interpreter, PCI discovery/config helpers, APIC/MP globals from `mp.h`, memory mapping/reservation, HPET, EC, and generic i8253/i8259 helpers.

Notable risks:
- Fixed arrays track at most 64 visited/mapped ACPI tables.
- The AML PCI address resolver assumes conventional `_ADR`, `_BBN`, bridge, and root-bridge semantics.
- ACPI memory access is powerful; safety relies on `memcheck()` and `#P/acpimem` permissions.
