# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/filesystem.c

This file creates the ext-family filesystem image used inside the linuxdisk plugin's GPT disk.

Key behavior:
- If size is not explicitly supplied, estimates source directory size using `du -c -k -s <dir> | tail -n1`.
- Adds 20 percent metadata overhead and enforces a 1 MiB minimum.
- Adds 32 MiB for ext3/ext4 journal overhead.
- Supports `size=+SIZE` by adding the estimate to the user-supplied extra size.
- Rounds final size to 512-byte sectors.
- Creates and truncates a temporary file, runs `mke2fs -q -F -t <type> [-L label] -d <dir> <file>`, unlinks it, and stores the fd/size in `struct virtual_disk`.

Dependencies:
- Uses `shell_quote` and `exit_status_to_nbd_error` for command safety/status handling.
- Reads globals from `virtual-disk.h`: `dir`, `label`, `type`, `size`, `size_add_estimate`.

Risks:
- Relies on external `du`, `tail`, and `mke2fs`.
- `type` validation happens in `linuxdisk.c`; this file passes it into the command.
- Size estimation is intentionally approximate.
