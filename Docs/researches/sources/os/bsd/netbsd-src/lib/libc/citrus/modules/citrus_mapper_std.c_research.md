# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.c

Read completely: 464 lines.

This module implements the standard binary-table mapper. It opens a mapped DB file, validates the `MAPPER\0\0` magic, reads the mapper `type`, and currently supports `rowcol` tables.

Key behavior: row/column metadata defines source component bit width, component ranges, destination unit width, invalid sentinel, and optional out-of-bounds/illegal-sequence extension. `rowcol_convert` decomposes the source index into row/column components, linearizes into a table offset, reads an 8/16/32-bit big-endian destination value, and returns success, non-identical, or illegal-sequence based on sentinel values.

Important interactions: uses `citrus_db` over an mmap-backed region, file-layout constants from `citrus_mapper_std_file.h`, local rowcol structures from `citrus_mapper_std_local.h`, and mapper ABI macros.

Security/reliability notes: it validates rowcol count, source bit width, destination unit width, and table size before conversion. Table-size multiplication uses `uint64_t`, reducing overflow risk. A likely validation bug exists in the optional extension block: after `_db_lookup_by_s` returns `ENOENT`, the code still checks `_region_size(&r) < sizeof(*eix)` before the `ret == 0` guard, using an uninitialized or stale region and potentially rejecting mapper files without the optional extension.
