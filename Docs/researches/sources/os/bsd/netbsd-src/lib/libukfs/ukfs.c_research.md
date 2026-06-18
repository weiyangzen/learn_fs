# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.c

Main implementation of `libukfs`, providing direct filesystem access through rump kernel VFS calls.

Key responsibilities:
- Initializes rump kernel support through `_ukfs_init`.
- Defines private `struct ukfs` with:
  - rump mount pointer,
  - rump lwp context,
  - device fd/path,
  - mount path,
  - current working directory,
  - partition object,
  - caller-specific pointer.
- Manages per-call rump context:
  - switches lwps,
  - creates file descriptor context,
  - chroots to mount path,
  - chdirs to saved cwd,
  - releases/switches back after calls.
- Parses partition selectors in device paths:
  - deprecated `%PART:`
  - `%DISKLABEL:x%`
  - `%OFFSET:start,end%`
- Opens and locks disk devices or image files using `fcntl` record locks.
- Registers disk/image devices with rump ETFS using partition offset and size.
- Mounts filesystems through `rump_sys_mount`.
- Handles MFS specially by mounting in a separate pthread.
- Releases mounts, ETFS registrations, locks, lwps, paths, and partition references.
- Implements filesystem operations:
  - directory open/read/close,
  - open/read/write/close,
  - create/mkdir/mknod/mkfifo/symlink/link/rename/remove/rmdir,
  - readlink,
  - chdir,
  - stat/lstat,
  - chmod/chown/chflags/utimes variants.
- Dynamically loads rump filesystem modules with `dlopen`.
- Scans module directories for `librumpfs_*.so`.
- Queries available VFS types through rump sysctl.
- Provides utility recursive directory creation.

Important notes:
- Many wrappers use `PRECALL`/`POSTCALL` to establish the correct rump namespace.
- `ukfs_read_fd`, `ukfs_write_fd`, and `ukfs_close` operate directly on rump file descriptors.
- `ukfs_part_release` reference-counts partition objects and avoids freeing singleton sentinel partitions.

Role in subsystem:
- Core user-facing filesystem API for mounting and manipulating filesystems via rump without normal host syscalls against the mounted image.
