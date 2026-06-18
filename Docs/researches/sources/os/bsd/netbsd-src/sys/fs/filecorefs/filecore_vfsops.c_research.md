# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vfsops.c

Read completely: 594 lines.

Implements FileCoreFS VFS operations and module registration. `filecore_vfsops` registers mount, unmount, root, statvfs, sync, vget/loadvnode, file-handle conversion, init/reinit/done, and vnode operation descriptors. A sysctl node is created for the filesystem.

`filecore_mount()` is read-only, supports `MNT_GETARGS`, resolves and authorizes the block device, and delegates new mounts to `filecore_mountfs()`. Updates only verify the same device. `filecore_mountfs()` invalidates old buffers, opens the device, reads and validates the FileCore boot block checksum, extracts the disc record, computes the map location, rereads the map’s boot block/disc record, builds `struct filecore_mnt`, computes block size, id geometry, mask, total block count, uid/gid policy, and mount stat fields.

Unmount flushes vnodes, clears mountedfs on the device vnode, closes the device, frees the mount, and clears `MNT_LOCAL`. Root lookup returns the synthetic `FILECORE_ROOTINO` vnode. `filecore_statvfs()` reports block geometry and total blocks but not free/file counts.

File handles carry only the synthetic inode number. `filecore_fhtovp()` rejects stale nodes whose copied directory entry name is empty; `filecore_vptofh()` serializes the inode into the handle.
