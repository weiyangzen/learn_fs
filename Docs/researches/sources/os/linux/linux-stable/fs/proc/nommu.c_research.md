# File Research: sources/os/linux/linux-stable/fs/proc/nommu.c

Creates global NOMMU `/proc/maps` for kernel-known memory regions.

Key points:
- Iterates `nommu_region_tree` under `nommu_region_sem`.
- Formats each `vm_region` like a maps line: start/end, permissions, offset, dev, inode, and optional file path.
- Registers `/proc/maps` only in NOMMU builds through `fs_initcall`.

Dependencies/contracts:
- Separate from per-process NOMMU maps in `task_nommu.c`.
- Exposes the flat NOMMU region list.
