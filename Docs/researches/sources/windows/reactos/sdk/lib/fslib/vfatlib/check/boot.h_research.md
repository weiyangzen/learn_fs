# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.h

This header declares boot-sector checker entry points.

Contents:
- `read_boot(DOS_FS *fs)` initializes filesystem geometry from the open device.
- `write_label(DOS_FS *fs, char *label)` declares volume label writing.
- `find_volume_de(DOS_FS *fs, DIR_ENT *de)` declares lookup of an existing volume-label directory entry.

Risk points:
- In `boot.c`, label-writing and `find_volume_de` implementations are excluded for ReactOS, so declarations may not correspond to compiled symbols under `__REACTOS__`.
- Depends on `DOS_FS` and `DIR_ENT` definitions from included checker headers.
