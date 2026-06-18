# File Research: sources/os/linux/linux-stable/fs/isofs/joliet.c

Implements Joliet Unicode filename conversion.

Key paths:
- `uni16_to_x8()` converts big-endian UTF-16 characters through a loaded NLS table, substituting `?` on conversion failure.
- `get_joliet_filename()` converts the directory-record name to UTF-8 when no NLS table is loaded, otherwise uses `uni16_to_x8()`. It strips trailing `;1` and trailing periods.

Important behavior:
- Joliet names are stored as big-endian 16-bit characters.
- Output is written into a page-sized temporary buffer supplied by callers in directory iteration and lookup.
