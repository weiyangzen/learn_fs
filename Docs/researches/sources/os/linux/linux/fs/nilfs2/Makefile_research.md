# File Research: sources/os/linux/linux/fs/nilfs2/Makefile

The NILFS2 `Makefile` builds `nilfs2.o` when `CONFIG_NILFS2_FS` is enabled. The composite object includes core inode/file/directory/superblock/name/page metadata code, block tree/direct mapping components, DAT/recovery, segment construction, checkpoint/sufile/ifile allocators, garbage-collection inode support, ioctl, and sysfs support.

Files listed into `nilfs2-y` include this group’s `alloc.o` and `bmap.o`, placing the persistent allocator and block mapping layer in the core NILFS2 module.
