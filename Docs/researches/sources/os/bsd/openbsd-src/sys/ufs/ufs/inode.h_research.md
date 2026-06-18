# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/inode.h

Read completely: 344 lines.

Defines the in-core UFS inode, filesystem-specific vtable hooks, dinode access macros, inode flags, indirect-block path structure, vnode conversions, and file-handle layout.

Core definitions:
- `struct inode` stores hash linkage, vnode, mount, flags, device/inode identity, effective link count, FFS/ext2 filesystem pointer, cluster info, quota pointers, NFS revision, lock state, inode rwlock, directory lookup side-effect fields, extension union for ext2 or dirhash, dinode pointer union, and operation vtable.
- `struct inode_vtbl` abstracts filesystem-specific truncate, update, inode allocation/free, buffer allocation, and buffer-at-offset operations.
- `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_INODE_ALLOC`, `UFS_INODE_FREE`, `UFS_BUF_ALLOC`, and `UFS_BUFATOFF` dispatch through that vtable.
- Defines UFS1/UFS2/ext2 field aliases and `DIP()`/`DIP_ASSIGN()`/`DIP_ADD()`/`DIP_AND()`/`DIP_OR()` for UFS1/UFS2 field selection.
- Defines inode flags for pending timestamp updates, modification, rename, locks, lazy modification, and hash membership.
- `struct indir` carries logical indirect-block paths for bmap/truncate; `struct ufid` overlays file handles.

Integration and risks:
- `DIP()` does not cover ext2, so callers must special-case ext2 where needed.
- Directory lookup writes state into the inode (`i_offset`, `i_count`, etc.), so callers must preserve locking assumptions.
- `i_effnlink` intentionally differs from on-disk link count during pending directory operations.
