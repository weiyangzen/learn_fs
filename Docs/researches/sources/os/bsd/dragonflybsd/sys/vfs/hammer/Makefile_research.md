# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/Makefile

This is the kernel module makefile for DragonFlyBSD HAMMER. It declares `KMOD= hammer` and lists the C source files compiled into the HAMMER filesystem module.

Included subsystems:
- VFS and vnode operations: `hammer_vfsops.c`, `hammer_vnops.c`.
- Core object/inode/cursor/B-Tree code: `hammer_inode.c`, `hammer_object.c`, `hammer_cursor.c`, `hammer_btree.c`.
- On-disk and I/O machinery: `hammer_ondisk.c`, `hammer_io.c`, `hammer_blockmap.c`, `hammer_undo.c`, `hammer_redo.c`.
- Transactions, recovery, and flushing: `hammer_transaction.c`, `hammer_recover.c`, `hammer_flusher.c`.
- Admin/reorganization features: ioctl, reblock, rebalance, mirror, pseudofs, prune, volume, dedup.
- Kernel trace option header: `opt_ktr.h`.

The file ends by including DragonFly’s standard kernel-module build rules through `<bsd.kmod.mk>`.
