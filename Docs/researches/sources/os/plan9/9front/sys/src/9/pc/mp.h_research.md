# File Research: sources/os/plan9/9front/sys/src/9/pc/mp.h

Defines data structures, constants, and external interfaces for Intel MultiProcessor Specification and APIC support.

Content summary:
- Raw MP floating pointer and configuration table structures: `_MP_`, `PCMP`, `PCMPprocessor`, `PCMPbus`, `PCMPioapic`, `PCMPintr`, and extended entries for address-space mapping, bus hierarchy, and compatibility bus address-space modifiers.
- Size macros for each packed table format.
- Enumerations for MP table entry types, processor/I/O APIC flags, interrupt polarity, trigger mode, interrupt types, address-space types, and bus hierarchy modifiers.
- Condensed runtime topology structures:
  - `Bus`: bus type, bus number, default polarity/trigger, interrupt list.
  - `Aintr`: links an MP interrupt entry to an APIC and bus.
  - `Apic`: APIC identity, mapped registers, flags, I/O APIC redirection metadata, local interrupt slots, `machno`, and online state.
- APIC register and redirection-entry bit constants.
- External declarations for I/O APIC, LAPIC, MP initialization, interrupt assignment, and global topology arrays.

Research notes:
- This is a contract header shared by MP table parsers, ACPI code, LAPIC/I/O APIC code, and `mp.c`.
- It contains no executable logic, but it controls how interrupt routing metadata is represented for device drivers.
- `MaxAPICNO` is 254 because 255 is reserved for physical broadcast.
