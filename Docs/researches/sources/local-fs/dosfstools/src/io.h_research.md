# File Research: sources/local-fs/dosfstools/src/io.h

Public interface for virtual filesystem/device I/O.

Declared operations:
- `fs_open`
- `fs_read`
- `fs_test`
- `fs_write`
- `fs_close`
- `fs_changed`

Role:
- Abstracts all on-disk reads/writes for fsck and fatlabel.
- Supports both immediate and queued write semantics through `write_immed`.
