# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.h

This header defines shared linuxdisk plugin state and APIs.

Key definitions:
- Extern configuration globals: `dir`, `label`, `type`, `size`, and `size_add_estimate`.
- Extern `random_state` used for partition GUID generation.
- `SECTOR_SIZE` is 512.
- `struct virtual_disk` contains regions, protective MBR, primary/secondary GPT headers, GPT partition table, filesystem size, partition GUID, and temp filesystem fd.

Declared APIs:
- `init_virtual_disk`, `create_virtual_disk`, `free_virtual_disk`.
- `create_partition_table`.
- `create_filesystem`.

Integration:
- Shared by `linuxdisk.c`, `filesystem.c`, `partition-gpt.c`, and `virtual-disk.c`.
