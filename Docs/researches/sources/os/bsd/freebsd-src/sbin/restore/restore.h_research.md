# File Research: sources/os/bsd/freebsd-src/sbin/restore/restore.h

Purpose: central shared type and global-state declaration header for `restore`.

Contents:
- Declares command flags, dump maps, tape metadata, current command, terminal stream, byte-swap flags, and old inode format flag.
- Defines `struct entry`, the in-memory restore symbol-table node for files/directories/links.
- Defines entry types `LEAF`, `NODE`, `LINK` and flags such as `EXTRACT`, `NEW`, `KEEP`, `REMOVED`, `TMPNAME`, and `EXISTED`.
- Defines `struct context curfile`, describing the next file/header on tape with mode, ownership, timestamps, flags, device, size, extattr size, inode, and name.
- Defines `RST_DIR`, `FORCE`, inode bitmap macros `TSTINO`/`SETINO`, conditional `dprintf`/`vprintf`, and status constants.

Integration: every restore source file depends on this header for the shared model. The `entry` graph and `curfile` context are the main internal contracts between tape reading, directory scanning, symbol-table operations, and extraction.

Risk notes: global variables and macros make state dependencies implicit. Bitmap macros assume valid inode ranges and map allocation sized by `maxino`.
