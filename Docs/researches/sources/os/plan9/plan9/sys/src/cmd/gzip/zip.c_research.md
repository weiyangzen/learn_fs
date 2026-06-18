# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.c

Plan 9 ZIP archive writer.

- Supports `zip [-vD] [-1-9] [-f zipfile] file ...`.
- Recursively archives directories, writing directory entries with trailing slash names.
- Writes local file headers, deflated file payloads, optional data descriptors for stdout archives, central directory entries, and end-of-central-directory record.
- Uses Plan 9 `<flate.h>` deflate callbacks and CRC-32 from `mkcrctab(ZCrcPoly)`/`blockcrc`.
- Stores modification times in MS-DOS time/date format and uses DOS-style external attributes.
- Maintains all `ZipHead` records in a growable in-memory array until the central directory is written.

Dependencies are `zip.h`, `bio`, `flate`, libc file APIs, and stdio-like Plan 9 functions.

Notable concerns:
- The archive is limited to fewer than 65536 entries and 32-bit ZIP sizes/offsets.
- Directory recursion constructs child paths in a fixed “parent + 256” allocation.
- It does not preserve full Unix permissions; attributes are DOS-oriented.
