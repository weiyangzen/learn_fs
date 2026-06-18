# File Research: sources/local-fs/udftools/include/libudffs.h

Main shared libudffs header.

Defines filesystem construction flags:
- Space accounting variants: freed/unallocated bitmap/table.
- Character encoding modes.
- Strategy 4096 and blank-terminal behavior.
- Closed/VAT/EFE/no-write modes.
- Boot-area preserve/erase/MBR modes.

Defines the in-memory UDF planning model:
- `struct udf_disc`: global UDF build state, descriptor pointers, partition maps, VAT state, metadata maps, root extent list, write callback, IDs, permissions, and counters.
- `struct udf_extent`: typed contiguous block range in the build plan.
- `struct udf_desc`: descriptor attached to an extent.
- `struct udf_data`: payload list for a descriptor.

Defines MBR boot-area structures and constants.

Exports APIs implemented by:
- `crc.c`: `udf_crc`.
- `extent.c`: extent/descriptor/data list management.
- `unicode.c`: encode/decode helpers for UDF strings.
- `misc.c`: app name, UUID extraction, strict integer parsing, random value, EINTR-safe I/O.

Key role: common contract between mkudffs, cdrwtool, and libudffs.
