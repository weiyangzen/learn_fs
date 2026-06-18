# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_int.h

Read completely: 102 lines.

Purpose: declares devfs internals shared only by `kern/kern_conf.c` and devfs implementation files.

Key structures:
- `struct cdev_privdata` stores per-file cdev private data, destructor, associated `struct file`, and list link.
- `struct cdev_priv` embeds the public `struct cdev` plus active-list links, inode, flags, in-use count, per-mount dirent array, destructor callback state, fd-private data list, destructor count, and thread lock.

Important flags:
- `CDP_ACTIVE` means the cdev is live.
- `CDP_SCHED_DTR` and `CDP_UNREF_DTR` relate to destructor scheduling.
- `CDP_ON_ACTIVE_LIST` tracks membership in `cdevp_list`.

Key declarations:
- cdev allocation/create/destroy/free helpers.
- dirent directory ref/unref and path containment helpers.
- global locks and lists: `devfs_inos`, `devmtx`, `devfs_de_interlock`, `cdevpriv_mtx`, `cdevp_list`.

Research notes:
- `cdev2priv()` is the core container conversion from public `struct cdev` to devfs-owned private state.
