# File Research: sources/os/linux/linux/fs/jffs2/jffs2_fs_sb.h

This header defines JFFS2 superblock-private state and mount options.

`struct jffs2_mount_opts` records compression override settings and reserved-pool size options. The reserved pool limits non-root writes when available space falls below `rp_size`.

`struct jffs2_sb_info` is the filesystem control structure. It stores the MTD device, inode numbering/check state, mount flags, GC thread state, allocation mutex, cleanmarker size, global flash space accounting, reserve thresholds, eraseblock array, current allocation and GC blocks, and all block-state lists: clean, very dirty, dirty, erasable, pending writebuffer erase, erasing, erase checking, erase pending, erase complete, free, bad, and bad-used.

It also contains erase synchronization (`erase_completion_lock`, `erase_wait`, `erase_free_sem`), inocache hash table and lock/waitqueue, NAND/writebuffer fields under `CONFIG_JFFS2_FS_WRITEBUFFER`, summary state, xattr subsystem state under `CONFIG_JFFS2_FS_XATTR`, mount options, and OS-private superblock linkage.

This structure is the shared state mutated by mount/build, write allocation, GC, erase, statfs, remount, and debug accounting checks. Space-accounting fields must sum to `flash_size`.
