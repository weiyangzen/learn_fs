# File Research: sources/os/bsd/dragonflybsd/sys/sys/mount.h

Primary DragonFly VFS mount interface. Defines file system ids, file handles, `statfs`, BIO dependency callbacks, quota accounting trees, the central `struct mount`, mount/user/kernel flags, mount-list scan flags, VFS sysctl IDs, MP-lock helper macros, sync flags, export/public NFS structures, `vfsconf`, VFS implementation flags, vfsquery flags, VFS operation typedefs, `struct vfsops`, dispatch macros, `VFS_SET`, export structures, and kernel/user VFS APIs.

Important filesystem details: `struct mount` stores VFS ops, vfsconf, namecache generation, syncer vnode/context, vnode lists, mount lock/token, stat/statvfs caches, mountpoint handles, VOP operation stacks for coherency/journaling/normal/spec/fifo, active journal list and stream id bitmap, BIO ops, rename lock, and VFS accounting. This is the core contract every filesystem implementation must satisfy.
