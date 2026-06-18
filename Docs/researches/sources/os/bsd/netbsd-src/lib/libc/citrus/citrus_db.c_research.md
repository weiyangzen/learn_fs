# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.c

Reader for Citrus compiled key/value database files.

Key behavior:
- `_citrus_db_open` validates magic, header, entry offset, and entry-directory bounds over a mapped region.
- `_citrus_db_lookup` hashes a key, walks collision chains, verifies key length and bytes, and returns a region for matching data.
- Locator support allows repeated lookup of duplicate/colliding entries.
- String and 8/16/32-bit typed lookup helpers validate data size and decode big-endian integer values.
- `_citrus_db_get_number_of_entries` and `_citrus_db_get_entry` provide sequential access.

Format:
- Uses `_citrus_db_file.h` big-endian on-disk header/entry records.
- Data/key regions are borrowed from the mapped database; caller must keep the underlying mapping alive.
