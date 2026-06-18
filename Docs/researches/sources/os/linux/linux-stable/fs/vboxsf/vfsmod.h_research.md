# File Research: sources/os/linux/linux-stable/fs/vboxsf/vfsmod.h

Private vboxsf module header. It includes the host ABI header and declares shared constants, private structs, operation tables, and cross-file helper prototypes.

Key private state:
- `vboxsf_options`: mount options for TTL, uid/gid, forced modes, and masks.
- `vboxsf_fs_context`: fs_context private parser state.
- `vboxsf_sbi`: per-superblock data including options, root host info, inode IDR, NLS table, root handle, and BDI id.
- `vboxsf_inode`: per-inode state with `force_restat`, open handle list, mutex, and embedded VFS inode.
- Directory buffer containers used to store host listing results.

The header defines `VBOXSF_SBI()` and `VBOXSF_I()` accessors and exposes the internal division between directory, file, utility, and host-wrapper modules.
