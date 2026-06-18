# File Research: sources/os/linux/linux/fs/afs/dir_silly.c

Purpose: implements AFS sillyrename behavior for unlinking or replacing busy open files on a stateless server.

Key interfaces:
- `afs_sillyrename()`.
- `afs_silly_iput()`.

Implementation notes:
- Busy unlink/rename targets are renamed in the same directory to hidden names of the form `.__afs%04X`, matching salvager expectations.
- Sillyrename uses the normal FS/YFS rename operation, marks the original dentry with `DCACHE_NFSFS_RENAMED`, stores the key on the directory vnode, and locally edits the directory cache by removing the old name and adding the silly name when data-version deltas match.
- On success, the dentry is moved to the silly name and the vnode gets `AFS_VNODE_SILLY_DELETED`.
- On final dentry inode put, `afs_silly_iput()` allocates/coordinates a parallel dentry, marks lock state deleted, then sends FS/YFS remove-file to delete the silly name.
- If lookup races find an alias, sillyrename state can be transferred to the alias dentry instead of immediately unlinking.

Dependencies:
- AFS operation framework, rename/remove-file RPCs, directory edit helpers, dentry locking, rmdir lock, key references, fsnotify/namei behavior inherited from NFS-style sillyrename.

Edge cases:
- A dentry already silly-renamed returns `-EBUSY`.
- If the generated hidden name lookup fails, the operation returns that error rather than risking deletion of an in-use file.
- `-ERESTARTSYS` after rename causes both dentries to be dropped because the server result is unknown.
