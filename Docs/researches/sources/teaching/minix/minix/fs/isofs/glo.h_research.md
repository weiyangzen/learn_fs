# File Research: sources/teaching/minix/minix/fs/isofs/glo.h

This header declares isofs globals, with `_TABLE` controlling definition.

Globals:
- `fs_dev`: current device handled by the server.
- `opt`: global mount/server options.
- `isofs_table`: fsdriver dispatch table.

Role:
- Minimal shared global state for the read-only ISO9660 server.
