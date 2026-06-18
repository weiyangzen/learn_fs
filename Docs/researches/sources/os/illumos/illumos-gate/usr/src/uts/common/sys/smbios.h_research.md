# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios.h

## Role

Defines the unstable illumos SMBIOS access API shared by `libsmbios` and the kernel SMBIOS module. It covers SMBIOS entry points, DMTF structure type IDs, decoded structure records, enumeration constants, access functions, formatting helpers, and kernel snapshot globals.

## Entry Points and Types

- `smbios_entry_point_t` distinguishes SMBIOS 2.1 and 3.0 entry point formats.
- Packed `smbios_21_entry_t` and `smbios_30_entry_t` mirror the DMTF table entry point layouts.
- `smbios_entry_t` unions the two entry point formats.
- Defines entry anchor strings, maximum entry length, standard structure types 0 through 46, inactive/end-of-table types, OEM range, and Sun/Oxide OEM extension type IDs.

## Decoded Records

The file defines decoded structures for BIOS, system, baseboard, chassis and chassis elements, processor, cache, port, slot and slot peers, onboard devices, language, event log, memory arrays/devices/maps, pointing devices, batteries, hardware security, voltage/cooling/temperature/current probes, boot status, management devices/components, IPMI, power supplies, additional information, extended onboard devices, TPM, processor additional information including RISC-V details, firmware inventory, string properties, and OEM processor/port/PCIe/memory extensions.

## Constants and Enumerations

Large groups of constants encode DMTF values for BIOS flags, wake events, board/chassis classes, processor families/upgrades/characteristics, cache types, connector/port/slot kinds, memory technologies and capabilities, probes, power supplies, TPM characteristics, RISC-V ISA/privilege/width, firmware state/formats, and string property IDs. `SMB_VERSION` currently maps to SMBIOS 3.9.

## Access API

- Open sources: `smbios_open()`, `smbios_fdopen()`, `smbios_bufopen()`.
- Buffer/checksum/write/close helpers.
- Error and truncation helpers.
- Lookup and iteration: `smbios_lookup_id()`, `smbios_lookup_type()`, `smbios_iter()`.
- Information functions decode each supported SMBIOS structure into the typed records above.
- Free helpers release allocated arrays for chassis elements, slot peers, extended memory chip-selects, additional info entries, and firmware components.
- `smbios_psn()` and `smbios_csn()` return product and chassis serial numbers.
- Userland-only `*_desc()` and `*_name()` helpers convert enumeration values to human-readable strings or macro names.
- Kernel exports `ksmbios` and `ksmbios_flags`.

## Risk Notes

This header is intentionally unstable, but it is still a broad ABI between the parser, utilities, and kernel consumers. Packed entry-point layouts, handle constants, version negotiation, decoded struct fields, and free-function ownership rules must stay synchronized with parser implementation and generated string tables.
