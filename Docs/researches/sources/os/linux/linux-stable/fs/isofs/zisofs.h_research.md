# File Research: sources/os/linux/linux-stable/fs/isofs/zisofs.h

Header for optional compressed ISOFS support.

Under `CONFIG_ZISOFS`, it declares:
- `zisofs_aops`
- `zisofs_init()`
- `zisofs_cleanup()`

This keeps compressed-file address-space operations and zlib workspace lifecycle separate from the base ISOFS code.
