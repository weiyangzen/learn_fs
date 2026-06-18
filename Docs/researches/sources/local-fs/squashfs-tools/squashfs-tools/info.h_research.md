# File Research: sources/local-fs/squashfs-tools/squashfs-tools/info.h

Header for signal-driven mksquashfs diagnostics.

Exports:
- `disable_info()`
- `update_info(struct dir_ent *)`
- `init_info()`

Key role: lets scanning/build code update the currently processed entry and initialize diagnostic signal handling.
