# File Research: sources/os/linux/linux-stable/fs/nilfs2/Makefile

Purpose: builds the NILFS2 filesystem module/object set when `CONFIG_NILFS2_FS` is enabled.

Key structures and state:
- Adds `nilfs2.o` to `obj-$(CONFIG_NILFS2_FS)`.
- Defines the `nilfs2-y` object list.

Major logic:
- Builds NILFS2 from inode, file, directory, superblock, namei, page, metadata-file, btnode, bmap, btree, direct, dat, recovery, core filesystem, segment buffer/segment, checkpoint file, segment usage file, inode file, allocator, GC inode, ioctl, and sysfs objects.

Concurrency and lifetime:
- No runtime code.

Important dependencies:
- The object list makes `alloc.o` and `bmap.o` part of the NILFS2 module covered by this group.

Risk/edge cases:
- Object ordering is conventional kernel build metadata; missing an object would produce unresolved symbols or feature loss.
