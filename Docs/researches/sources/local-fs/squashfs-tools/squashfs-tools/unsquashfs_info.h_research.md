# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.h

Minimal header for the extraction info thread.

Exports:
- `disable_info()`
- `update_info(char *)`
- `init_info()`

Used by `unsquashfs.c` to initialize interactive status reporting and update the current extraction pathname.
