# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vfsops.c

Tmpfs VFS operations and module glue: mount/remount/unmount, root lookup, statvfs, fid-to-vnode lookup, global limits, and module lifecycle.

Key responsibilities:
- Defines tmpfs module linkage and `vfsdef_t`, with mount options `xattr`, `noxattr`, `size`, and `mode`.
- Registers VFS and vnode operations in `tmpfsinit()`, initializes directory hashing, tmpfs resource limits, unique device major/minor state, and tmpfs globals.
- Handles `_init`, `_fini`, and `_info` module entry points.
- Implements `tmp_mount()` with mount permission checks, mountpoint busy checks, read-only rejection, size/mode parsing, remount size updates, tmount allocation, unique device selection, root tmpnode creation, mountpoint attribute inheritance, and root directory initialization.
- Implements `tmp_unmount()` with forced-unmount rejection, busy checks, tmpnode hold scanning, directory-entry truncation pass, node-release pass, xattr cleanup, mount-path/free-space assertions, mutex destruction, and tmount free.
- Implements `tmp_root()` by holding and returning the root vnode.
- Implements `tmp_statvfs()` from system/zone swap availability, per-mount anon use/limit, tmpfs kernel-memory headroom, device id, mount path, and flags.
- Implements `tmp_vget()` by scanning the tmpnode list for matching fid inode/generation, holding the vnode if still linked, and restoring `VISSWAP` for sticky non-directory swap-like files.

Dependencies:
- Uses tmpnode, tmp directory, and tmp option parsing helpers from other tmpfs files.
- Uses anon accounting, zone swap caps, vfs option helpers, pathname APIs, vnode lifecycle helpers, and kernel module/VFS registration APIs.

Concurrency and locking:
- `tmpfs_minor_lock` serializes unique tmpfs minor allocation.
- `tm_contents` protects mount-wide tmpnode list and anon accounting.
- `tmp_unmount()` holds tmpnodes while checking for busy references and releases them in a controlled reverse traversal.
- Root tmpnode initialization takes the root `tn_rwlock` while setting `VROOT`, inherited attributes, list pointers, and directory entries.

Notable risks:
- Remount only updates `tm_anonmax`; lowering below current usage is allowed and makes the filesystem full until usage drops.
- `tmp_statvfs()` must report zone-aware capacity when non-global zones or swap caps are involved.
- Unmount relies on `tmp_inactive()` eventually removing nodes held by pageout or anon slots; it waits and retries when the tail node remains.
