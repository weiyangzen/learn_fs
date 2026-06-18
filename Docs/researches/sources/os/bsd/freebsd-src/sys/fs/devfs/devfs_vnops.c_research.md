# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_vnops.c

Read completely: 2181 lines.

Purpose: implements devfs vnode and file operations for synthetic directories/symlinks and character devices, including lookup, open/close, read/write/ioctl/poll/kqueue/mmap delegation to `cdevsw`, controlling terminal handling, and per-file cdev private data.

Key support systems:
- `devfs_de_interlock` protects vnode/dirent association and use-count updates.
- `cdevpriv_mtx` protects per-file cdev private data lists.
- `devfs_timestamp()` updates timestamps cheaply unless `vfs.devfs.dotimes` is enabled.

Per-file cdev private data:
- `devfs_get_cdevpriv()`, `devfs_set_cdevpriv()`, `devfs_foreach_cdevpriv()`, `devfs_destroy_cdevpriv()`, and `devfs_clear_cdevpriv()` support drivers storing per-open state with destructors.

Vnode allocation/population:
- `devfs_populate_vp()` ensures a vnode’s mount tree is current, dropping the vnode lock around `devfs_populate()` when needed.
- `devfs_allocv()` creates or returns a vnode for a dirent, handles existing vnode races, assigns VCHR/VDIR/VLNK/VBAD type, references cdevs, selects `devfs_specops` for character devices, associates MAC labels, and handles doomed dirents/mount finalization.

Lookup/name behavior:
- `devfs_lookup()` and `devfs_lookupx()` support normal lookup, `.`/`..`, directory execute checks, clone-on-lookup through the `dev_clone` eventhandler, whiteout/covered filtering, jail visibility checks, and create/delete behavior.
- `devfs_fqpn()` constructs mount-relative full paths.
- `devfs_vptocnp()` resolves vnode-to-component names and parent vnode references.

Character-device operations:
- `devfs_open()` validates cdev, tracks usecount, calls `d_fdopen` or `d_open`, sets `f_data`, and swaps fileops to `devfs_ops_f`.
- `devfs_close()` handles controlling terminal refs, last-close detection, forced revoke flags, `D_TRACKCLOSE`, and calls driver `d_close`.
- Fileops `devfs_read_f()`, `devfs_write_f()`, `devfs_ioctl_f()`, `devfs_poll_f()`, `devfs_kqfilter_f()`, and `devfs_mmap_f()` validate the cdev via `devfs_fp_check()` and delegate to driver methods.
- `devfs_ioctl()` handles `FIODTYPE`, `FIODGNAME`, driver ioctls, `ENOIOCTL` translation, and `TIOCSCTTY` controlling-terminal assignment.

Directory/symlink operations:
- `devfs_readdir()` populates, skips covered/whiteout/jail-hidden entries, emits synthetic dirents, and reports EOF.
- `devfs_symlink()` requires `PRIV_DEVFS_SYMLINK`, creates user symlinks, can cover existing generated entries, references directories, applies rules, and allocates a vnode.
- `devfs_remove()` removes user symlinks or whiteouts generated devices.
- `devfs_readlink()` returns stored symlink target.

Reclaim/revoke:
- `devfs_reclaim()` detaches generic dirents from vnodes.
- `devfs_reclaim_vchr()` also releases cdev references and usecounts.
- `devfs_revoke()` revokes all vnodes associated with a cdev across mount dirent arrays and handles inactive cdev garbage collection.

VOP/fileops vectors:
- `devfs_vnodeops` handles non-character devfs nodes.
- `devfs_specops` handles VCHR nodes, with actual I/O routed through fileops after open.
- `devfs_ops_f` is the character-device fileops table.

Research notes:
- This is the highest-risk devfs file: it coordinates VFS locks, devfs mount locks, cdev refs, file private data, session/tty state, and driver callbacks.
- Jail checks and rules/whiteouts define what users actually see under `/dev`.
