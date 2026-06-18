# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/recover.c

Implements the live `do_recover` path for recovering file contents from saved item maps.

The older stdin text-map recovery implementation is disabled with `#if 0`. A second older binary map reader is also commented out.

Live behavior:
- Reads `struct saved_item` records from `map_file(fs)` or stdin.
- Opens `recovery_file(fs)` for output.
- Reconstructs a file by reading each saved item’s source block and item index.
- For direct items, writes item body bytes at key offset.
- For indirect items, reads each unformatted block pointer and writes pointed block data.
- Handles overlapping/problem item ranges interactively by printing candidate items and asking which should be left.

Dependencies:
- Uses `struct saved_item` from `debugreiserfs.h`.
- Uses item/key helpers from `reiserfscore`.

Notable risks/quirks:
- The saved-item file is raw native struct data minus the pointer field, so it is ABI/endian/layout fragile.
- Uses interactive stdin selection for overlaps.
- Opens recovery output with `"w+"`, truncating existing files.
