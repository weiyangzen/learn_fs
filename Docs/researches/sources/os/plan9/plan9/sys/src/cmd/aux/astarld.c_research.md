# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/astarld.c

This file loads firmware or memory images into an `astar` device.

Key behavior:
- Supports Intel HEX-style load records and raw image loading.
- Opens `#G/astarNctl` and `#G/astarNmem`, requests `download`, writes memory, then optionally sends `run`.
- Can operate on a temporary local file instead of hardware with `-n`.
- Clears the 64 KiB target memory before loading hex input.
- Verifies writes by reading memory back and comparing.

Important details:
- Supports device units `-0` through `-3`.
- Parses data, EOF, and segment records with checksums.
- Enforces a 64 KiB memory limit.
- Options include dump, image, no-load, and no-start modes.

Filesystem relevance:
- Indirect: uses Plan 9 device files as firmware loading endpoints.
