# File Research: sources/os/linux/linux/fs/ramfs/Makefile

Build rules for ramfs.

Key behavior:
- Always builds `ramfs.o` into the kernel object list with `obj-y += ramfs.o`.
- Composes `ramfs.o` from `inode.o` and a file-operations object.
- Defaults `file-mmu-y` to `file-nommu.o`.
- Overrides `file-mmu-y` to `file-mmu.o` when `CONFIG_MMU` is enabled.

Research notes:
- This Makefile selects mutually exclusive MMU vs NOMMU file operation implementations while keeping common inode/superblock code in `inode.o`.
