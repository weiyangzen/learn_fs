# File Research: sources/os/linux/linux/fs/adfs/dir_f.c

Implements ADFS E/F fixed-size directory format handling.

Key behavior:
- Provides unaligned little-endian read/write helpers for 1-4 byte fields.
- Computes the F-format directory check byte by rotating/xoring directory words and tail data.
- Validates directory header/tail sequence fields, magic names (`Nick` or `Hugo`), reserved fields, and check byte.
- Reads fixed 2048-byte directories and sets header/tail pointers.
- Converts disk directory entries to `object_info`:
  - Name up to 10 visible characters.
  - 3-byte indirect disk address.
  - 4-byte load/exec/length.
  - Attribute byte.
- Converts `object_info` back to disk entry metadata for updates.
- Supports fixed-position scanning of up to 77 entries.
- Iteration emits entries until an empty name or the fixed entry limit.
- Update locates an entry by indirect address and rewrites its mutable fields.
- Commit increments directory sequence numbers, recomputes check byte, and revalidates.

Important interactions:
- Exported through `adfs_f_dir_ops`.
- Used for non-F+ ADFS disks selected in `super.c`.
