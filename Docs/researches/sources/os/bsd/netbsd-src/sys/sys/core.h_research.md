# File Research: sources/os/bsd/netbsd-src/sys/sys/core.h

Defines the traditional NetBSD core dump file header and segment header formats.

Key content:
- Magic constants: `COREMAGIC`, `CORESEGMAGIC`.
- `CORE_GETMAGIC`, `CORE_GETMID`, `CORE_GETFLAG`, `CORE_SETMAGIC` for packed network-byte-order `c_midmag`.
- Segment flags: `CORE_CPU`, `CORE_DATA`, `CORE_STACK`.
- `struct core` and `struct coreseg`.
- 32-bit variants: `struct core32`, `struct coreseg32`.

Important behavior:
- Includes `<sys/endian.h>` for `ntohl`/`htonl`.
- Uses `MAXCOMLEN` via included machine/a.out context.
- File format is ABI-visible to crash/core analysis tools.
