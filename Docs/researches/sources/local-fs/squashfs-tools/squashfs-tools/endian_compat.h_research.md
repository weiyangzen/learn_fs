# File Research: sources/local-fs/squashfs-tools/squashfs-tools/endian_compat.h

Portability shim for byte-order macros.

Behavior:
- On Linux, includes `<endian.h>`.
- On non-Linux systems, includes `<sys/types.h>` and maps:
  - `__BYTE_ORDER` to `BYTE_ORDER`
  - `__BIG_ENDIAN` to `BIG_ENDIAN`
  - `__LITTLE_ENDIAN` to `LITTLE_ENDIAN`

Key role: lets compressor option headers use Linux-style endian macros across platforms.
