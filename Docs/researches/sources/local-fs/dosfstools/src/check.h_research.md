# File Research: sources/local-fs/dosfstools/src/check.h

Public checker interface.

Declared functions:
- `check_dirty_bits(DOS_FS *fs)`
- `scan_root(DOS_FS *fs)`
- `check_label(DOS_FS *fs)`

Role:
- Exposes the repair engine entry points used by `fsck.fat.c`.
- Also lets `boot.c`/`fat.c` share checker-related declarations through the common source set.
