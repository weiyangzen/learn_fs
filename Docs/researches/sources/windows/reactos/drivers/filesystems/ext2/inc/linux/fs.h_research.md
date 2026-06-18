# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/fs.h

This header defines a minimal Linux VFS compatibility layer.

Key content:
- Device helpers and macros: `kdev_t`, `NODEV`, `MINORBITS`, `MINORMASK`, `MAJOR`, `MINOR`, `MKDEV`, `kdev_t_to_nr`, `to_kdev_t`.
- `struct super_block`: magic, flags, block size/max size, dirt flag, ID, block device, private VCB pointer, root dentry, and filesystem info pointer.
- `struct inode`: inode number, size/timestamps/delete time, block count/pointers, mode, uid/gid, refcount, link count, generation/version/flags, superblock pointer, private MCB pointer, extra inode size, and file ACL.
- Inode dirty/state bit masks.
- `struct dentry`: refcount, name, inode, parent, filesystem data, and superblock.
- `struct file`: flags, mode, version, size, position, dentry, and private data.
- Linux directory type constants.
- Prototypes: `iget`, `iput`, `bmap`.

Role:
- Provides just enough Linux VFS shape for borrowed ext3, htree, JBD, and ext4 extent/xattr code to compile inside the Windows driver.

Notable constraints:
- Device conversion helpers are stubbed to return `0`.
- The structures are simplified and do not provide full Linux VFS semantics.
