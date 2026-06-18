# File Research: sources/os/linux/linux/fs/jffs2/jffs2_fs_i.h

This header defines `struct jffs2_inode_info`, the JFFS2 private inode state embedded in each VFS inode.

The structure contains `sem`, an internal mutex used instead of relying solely on `inode->i_rwsem`, because GC needs locking behavior that avoids VFS inode semaphore deadlocks. It tracks `highest_version`, an rb-tree `fragtree` describing file data extents, optional `metadata` dnode for metadata-only inode data, linked-list `dents` for directories, symlink `target`, the permanent `inocache`, JFFS2 flags and user compression preference, and finally the embedded `struct inode vfs_inode`.

This is the core bridge between VFS inode lifetime and JFFS2’s append-only flash-node model. Regular file reads/writes, directory operations, GC, setattr, and readinode code all synchronize or mutate this structure.
