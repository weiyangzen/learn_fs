# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_kernel.h

This header defines the FUSE kernel/userspace wire protocol ABI. It is imported from the FUSE protocol lineage and carries dual GPL/Linux-syscall-note or BSD-2-Clause licensing for this interface header.

Key contents:
- Protocol changelog from FUSE 7.1 through 7.35.
- Protocol version constants:
  - `FUSE_KERNEL_VERSION 7`
  - `FUSE_KERNEL_MINOR_VERSION 35`
  - `FUSE_ROOT_ID 1`
- Core attribute/stat structures:
  - `struct fuse_attr`
  - `struct fuse_kstatfs`
  - `struct fuse_file_lock`
- Bitmasks for operation inputs and negotiated capabilities:
  - `FATTR_*` setattr valid bits.
  - `FOPEN_*` open result flags.
  - `FUSE_*` init capability flags, including async read, POSIX locks, export support, writeback cache, no-open/no-opendir support, setxattr extension, submounts, mapping, and newer killpriv behavior.
  - release, getattr, lock, write, read, ioctl, poll, fsync, fallocate, attr, open, and setxattr flag sets.
- `enum fuse_opcode`
  - Defines request opcodes from `FUSE_LOOKUP` through `FUSE_SYNCFS`.
  - Includes Linux-only CUSE values under `#ifdef linux`.
- `enum fuse_notify_code`
  - Defines notification opcodes for poll wakeup, inode invalidation, entry invalidation, store/retrieve, delete, and max marker.
- Request/reply structures for FUSE operations:
  - lookup replies: `fuse_entry_out`
  - forget/batch forget
  - getattr/attr out
  - mknod/mkdir/rename/link/setattr
  - open/create/open out
  - release/flush
  - read/write/write out
  - statfs
  - fsync
  - xattr get/list/set/remove support
  - locks
  - access
  - init in/out
  - interrupt
  - bmap
  - ioctl and ioctl iovecs
  - poll
  - fallocate
  - wire headers: `fuse_in_header`, `fuse_out_header`
  - directory entries: `fuse_dirent`, `fuse_direntplus`, alignment/size macros
  - notifications for invalidation/delete/store/retrieve
  - device clone ioctl
  - lseek
  - copy file range
  - setup/remove mapping
  - syncfs
- Compatibility size constants:
  - `FUSE_COMPAT_ENTRY_OUT_SIZE`
  - `FUSE_COMPAT_ATTR_OUT_SIZE`
  - `FUSE_COMPAT_MKNOD_IN_SIZE`
  - `FUSE_COMPAT_WRITE_IN_SIZE`
  - `FUSE_COMPAT_STATFS_SIZE`
  - `FUSE_COMPAT_SETXATTR_IN_SIZE`
  - `FUSE_COMPAT_INIT_OUT_SIZE`
  - `FUSE_COMPAT_22_INIT_OUT_SIZE`

Integration points:
- Included by the FreeBSD FUSE implementation through `fuse.h` and the internal files in this group.
- The dispatcher/audit code in `fuse_ipc.c` uses these structure sizes for protocol validation.
- Mount init negotiation in `fuse_internal.c` uses version and capability definitions.
- I/O, vnode, xattr, lock, and VFS code build these exact request payloads.

Notable risks and research hooks:
- This is ABI surface: structure layout, padding, integer widths, and alignment macros must remain wire-compatible.
- Some definitions are Linux/FreeBSD conditional; only common FUSE structures are active in this FreeBSD kernel build.
- FreeBSD implementation advertises or consumes only a subset of protocol features even though this header defines newer operations.
- Reply-size compatibility constants are essential for older daemon support.
