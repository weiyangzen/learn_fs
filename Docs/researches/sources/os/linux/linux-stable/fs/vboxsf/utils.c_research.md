# File Research: sources/os/linux/linux-stable/fs/vboxsf/utils.c

Provides vboxsf utility code for inode allocation/init, stat/revalidation, getattr/setattr, path conversion, NLS conversion, and directory buffer management.

`vboxsf_new_inode()` allocates Linux inodes and assigns synthetic inode numbers through an IDR, incrementing generation on wrap. `vboxsf_init_inode()` converts host `shfl_fsobjinfo` into Linux inode type, mode, ownership, size, blocks, timestamps, operations, and address-space ops, applying mount masks and forced modes.

Revalidation is host-stat based. `vboxsf_inode_revalidate()` honors the dentry TTL unless `force_restat` is set, restats the host object, reinitializes inode metadata, and invalidates the pagecache if mtime advanced. `vboxsf_getattr()` supports statx sync flags, while `vboxsf_setattr()` opens the object for attribute writes, separately updates mode/times and size through `vboxsf_fsinfo()`, then restats.

Path conversion builds `shfl_string` paths from dentries, converting from configured NLS to UTF-8 when needed. Directory helpers allocate 16 KiB buffers, collect all host directory entries with `vboxsf_dirinfo()`, and tolerate host filename translation failure (`-EILSEQ`) by treating it as nonfatal.
