# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_abi.h

Read completely: 825 lines.

Linux-compatible FUSE kernel/userspace ABI header. It defines protocol version 7.28, opcodes, flags, structure layouts, directory entry alignment macros, notification payloads, and `/dev/fuse` clone ioctl values.

The header documents protocol changes from FUSE 7.9 through 7.28. `FUSE_KERNEL_VERSION` is 7, `FUSE_KERNEL_MINOR_VERSION` is 28, and `FUSE_ROOT_ID` is 1.

Core structures include `fuse_attr`, `fuse_kstatfs`, `fuse_file_lock`, many operation-specific `*_in` and `*_out` request/reply payloads, `fuse_in_header`, `fuse_out_header`, `fuse_dirent`, and `fuse_direntplus`.

Flag groups cover setattr validity, open flags, init flags, CUSE flags, release/getattr/lock/write/read/ioctl/poll flags, and maximum ioctl iovec count.

`enum fuse_opcode` defines lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rename, link, open, read, write, statfs, release, fsync, xattrs, flush, init, opendir/readdir/releasedir, locks, access, create, interrupt, bmap, destroy, ioctl, poll, batch forget, fallocate, readdirplus, rename2, lseek, copy_file_range, and CUSE init.

Important dependencies: included by `fuse.h`, `fuse_debug.h`, `fuse_vfsops.c`, `fuse_device.c`, `fuse_ipc.c`, `fuse_util.c`, and vnode code.

Research notes: this file is ABI-sensitive and should not be casually edited. DragonFly reply auditing in `fuse_util.c` depends on these exact layouts.
