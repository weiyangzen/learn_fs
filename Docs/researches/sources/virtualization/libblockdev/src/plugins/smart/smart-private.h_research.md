# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart-private.h

This private header defines backend-shared SMART internals. It is not part of the public libblockdev API.

Contents:
- Includes GLib, GObject, `blockdev/utils.h`, and `smart.h`.
- Defines `_C_LOCALE` as `(locale_t) 0` for locale-neutral libc error formatting.
- Defines `DriveDBAttr`, a simple `{ id, name }` pair used with the optional compiled smartmontools drive database parser.
- Defines `struct WellKnownAttrInfo`, mapping an attribute ID to:
  - libatasmart-style well-known name,
  - libblockdev pretty-value unit,
  - a NULL-terminated list of accepted smartmontools names.

The large `well_known_attrs[256]` table is a conservative translation/validation table for ATA SMART attribute IDs. It covers common HDD and SSD IDs such as raw read error rate, spin-up time, reallocated sector count, power-on hours, temperature attributes, pending sectors, UDMA CRC errors, wear/endurance attributes, and LBA counters.

Declared internal functions:
- `_smart_close_plugin()` lets common close code call backend-specific cleanup.
- `drivedb_lookup_drive()` returns optional drive-specific attribute definitions.
- `free_drivedb_attrs()` frees drive DB lookup results.

Research relevance:
- This table is the semantic bridge between libatasmart names and smartmontools names.
- Both SMART backends use it to decide whether an attribute should receive a trusted `well_known_name`.
- The table intentionally does not solve all vendor-specific remapping and leaves some TODO entries.
