# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_vnops.c

Read completely: 2309 lines.

## Role

This file implements devfs vnode operations and optimized file operations for character-device vnodes. It covers directory/namecache behavior for the synthetic devfs tree, user-created directories and symlinks, permissions/attributes, device open/close, direct device read/write/ioctl/kqueue calls, disk safety checks, buffer strategy splitting, device getpages, and device-backed `stat`/`seek`.

## Main Responsibilities

- Define vnode operation tables:
  - `devfs_vnode_norm_vops` for directories, links, and synthetic non-device nodes.
  - `devfs_vnode_dev_vops` for character-device vnodes.
- Define `devfs_dev_fileops`, installed on opened device files to bypass generic vnode fileops for read/write/ioctl/kqueue/stat/seek/close.
- Implement normal devfs operations:
  - `devfs_vop_access()` checks visibility and uses helper permissions.
  - `devfs_vop_inactive()` recycles unlinked nodes.
  - `devfs_vop_reclaim()` detaches vnode/node/device associations and frees unlinked nodes.
  - `devfs_vop_readdir()` emits `.`, `..`, and visible children, with cookie support.
  - `devfs_vop_nresolve()` resolves children and follows devfs alias links up to a depth limit.
  - `devfs_vop_nlookupdotdot()` resolves parent directories.
  - `devfs_vop_getattr()` synthesizes attributes and reports disk media size for disk devices.
  - `devfs_vop_setattr()` changes uid/gid/mode and syncs override devices.
  - `devfs_vop_readlink()` reads user-created symlink text.
  - `devfs_vop_nmkdir()`, `devfs_vop_nsymlink()`, `devfs_vop_nrmdir()`, and `devfs_vop_nremove()` support user-created directories and links while protecting core-generated nodes.
- Implement device vnode open/close:
  - `devfs_spec_open()` handles quick devices, clone handlers, cloned vnode replacement, disk write restrictions, tty setup, VM object initialization for disks, pty visibility, and fileops replacement.
  - `devfs_spec_close()` decides when to call the device close method based on reclaim, tracking-close flags, and last-open detection.
  - `devfs_fo_close()` routes file close through `vn_close()` and clears cdev private data.
- Implement optimized device fileops:
  - `devfs_fo_read()` and `devfs_fo_write()` call `dev_dread()`/`dev_dwrite()` directly and maintain file offsets and sequential heuristics.
  - `devfs_fo_ioctl()` handles `FIODTYPE`, `FIODNAME`, delegates to `dev_dioctl()`, and updates controlling tty state for `TIOCSCTTY`.
  - `devfs_fo_stat()` builds `struct stat` from vnode/device attributes and device last-read/write times.
  - `devfs_fo_kqfilter()` delegates to `dev_dkqfilter()`.
  - `devfs_fo_seek()` implements regular seek semantics while allowing negative offsets for device address use.
- Implement device vnode operations:
  - `devfs_spec_fsync()` flushes dirty buffers for disk vnodes.
  - `devfs_spec_read()`/`devfs_spec_write()` call direct device methods for VOP paths.
  - `devfs_spec_ioctl()` and `devfs_spec_kqfilter()` delegate to device methods.
  - `devfs_spec_strategy()` converts vnode strategy to device strategy and splits oversized I/O into chained buffers when larger than `si_iosize_max`.
  - `devfs_spec_strategy_done()` completes chained I/O and propagates errors/short transfers.
  - `devfs_spec_freeblks()` issues synchronous free-block/TRIM-style requests for devices with `SI_CANFREE`.
  - `devfs_spec_bmap()` provides identity mapping for contiguous device offsets.
  - `devfs_spec_advlock()` rejects POSIX locks and reports unsupported for others.
  - `devfs_spec_getpages()` reads device data into VM pages using KVA pbuf mapping.

## Synchronization and Lifetime Model

- `devfs_lock` protects devfs node topology operations and alias/link resolution.
- Vnode locks are upgraded or released around slow device operations to avoid deadlocks and to allow driver callbacks.
- Device references are acquired around direct fileops before dereferencing `vp->v_rdev`.
- Reclaim handles being called with or without `devfs_lock` already held.
- Device close warns that the devfs node can disappear during `dev_dclose()` if the device destroys itself.
- `devfs_spec_open()` releases `devfs_lock` around clone-handler callbacks because drivers may call back into devfs.
- Buffer-strategy chunking uses a separate allocated buffer with a completion callback and preserves the original bio for final `biodone()`.

## Important Interactions

- Heavy dependency on `devfs_core.c`:
  - node accessibility
  - vnode allocation
  - clone creation
  - cdev private storage
  - topology updates
- Uses the character-device dispatch layer:
  - `dev_dopen()`
  - `dev_dclose()`
  - `dev_dread()`
  - `dev_dwrite()`
  - `dev_dioctl()`
  - `dev_dkqfilter()`
  - `dev_dstrategy()`
  - `dev_dstrategy_chain()`
- Integrates with generic VFS helpers:
  - `vop_helper_access()`
  - `vop_helper_chown()`
  - `vop_helper_chmod()`
  - `vop_stdopen()`
  - `vop_stdclose()`
  - `vfsync()`
  - `vinitvmio()`
  - `vfs_mountedon()`
  - `vn_stat()`
- Uses tty/session state for controlling terminal assignment.
- Uses VM and buffer-cache primitives for disk-backed getpages and strategy calls.

## Notable Design Details

- Device vnodes switch their file pointer to `devfs_dev_fileops` after open, so ordinary reads/writes avoid the VOP table.
- Disk devices opened for write are restricted by `securelevel` and existing read-write mounts.
- D_QUICK devices take a shorter open/close path and retain only a shared vnode lock.
- `FIODNAME` copies the device name to userland through a caller-supplied buffer descriptor.
- `devfs_vop_getattr()` uses `DIOCGPART` to report disk size so `lseek()` works properly.
- `devfs_spec_getpages()` zero-fills short reads so VM pages never expose stale KVA data.

## Research Notes

- This file is a major safety boundary: it must balance vnode locking, device driver callbacks, cdev references, session tty state, and buffer-cache/VM interactions.
- Last-close detection notes an SMP weakness because `count_dev()` is not fully safe across multiple vnodes referencing the same cdev.
- `devfs_vop_nremove()` and `devfs_vop_nrmdir()` only allow removal of `DEVFS_USER_CREATED` nodes, protecting kernel-generated device entries.
- Alias resolution and hidden-node checks are critical for rule enforcement.
