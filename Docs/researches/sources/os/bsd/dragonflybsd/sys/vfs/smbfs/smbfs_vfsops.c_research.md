# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_vfsops.c

This file registers the SMBFS VFS operations and implements mount, unmount, root, statfs, sync, init, and uninit.

Mount validates `NETSMB`, copies `smbfs_args`, checks the mount ABI version, resolves the userspace SMB device handle into an SMB share, allocates `struct smbmount`, initializes the per-mount vnode hash, stores credentials and mode/case settings, formats `f_mntfromname` as an SMB UNC-like source, installs vnode ops, and obtains the root vnode.

Unmount repeatedly calls `vflush` because SMBFS vnodes can hold parent references and may need more than one pass. It then releases the SMB share, credential, hash table, lock, and mount structure.

`root` creates or references the root smbnode by synthesizing root attributes through `smbfs_smb_lookup(NULL, NULL, ...)` and naming the root node `"TheRooT"`. `statfs` chooses TRANS2 or legacy SMB statfs based on dialect and fills VFS stat fields. `sync` walks dirty vnodes and invokes `VOP_FSYNC` except for locked, clean, or lazy-sync cases.

The file also declares sysctls for SMBFS version/debug level, module dependencies on `netsmb`, `libiconv`, and `libmchain`, and initializes the pbuf free count.
