# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/dump.c

Purpose: Formatting and diagnostic output helpers for `pdisk` Apple partition maps.

Main output paths:
- `dump_partition_map()` prints a concise partition table ordered by disk address, including type, name, length, base, driver marker, and scaled byte size.
- `dump_block_zero()` prints block zero device metadata and driver descriptors.
- `show_data_structures()` prints a more internal view: map sizing, writable/changed state, block zero fields, partition flags, logical ranges, and boot metadata.
- `full_dump_partition_entry()` prints every field for a selected partition entry, including reserved byte arrays via hex/ascii dump.
- `full_dump_block_zero()` prints every block zero field and reserved bytes.

Formatting helpers:
- `dump_partition_entry()` computes display widths from maximum type/name/base/length lengths.
- `dump_block()` prints 16-byte hex/ascii rows.
- `get_max_type_string_length()`, `get_max_name_string_length()`, and `get_max_base_or_length()` scan the map to support aligned output.
- Uses `fmt_scaled()` for human-readable sizes.

Integration:
- Depends on `partition_map.h` for `struct partition_map`, `struct entry`, flags, and lookup helpers.
- Called by interactive `pdisk` commands for normal, verbose, and detailed display modes.
