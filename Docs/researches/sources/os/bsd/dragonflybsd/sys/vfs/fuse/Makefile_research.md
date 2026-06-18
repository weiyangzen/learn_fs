# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/Makefile

Builds the DragonFlyBSD FUSE kernel module. It declares `KMOD=fuse` and compiles `fuse_vfsops.c`, `fuse_vnops.c`, `fuse_device.c`, `fuse_node.c`, `fuse_ipc.c`, `fuse_io.c`, and `fuse_util.c`.

The listed work item includes all makefile-listed FUSE sources except `fuse_vnops.c`, which is outside this group’s file list.

Important dependencies: standard `bsd.kmod.mk` kernel module build framework and the FUSE source files in this directory.

Notable risks or research hooks: build membership confirms that vnode operation behavior is split into `fuse_vnops.c`, so reports over this group should not treat the listed FUSE files as the whole FUSE implementation.
