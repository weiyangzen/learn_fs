# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specsubr.c

## Purpose
Implements core specfs special-vnode support: snode creation, common vnode lookup, device vnode association, snode hash management, device fencing, initialization, and special-device close helpers.

## Key Responsibilities
- `specvp` returns a shadow special vnode for a real device vnode, reusing an existing snode keyed by device/type/real vnode or creating a new one. FIFOs are redirected to `fifovp`.
- `specvp_devfs` wraps `specvp` and associates the common snode with a devinfo node.
- `makespecvp` creates a special vnode without a real vnode, commonly for device-oriented synthetic opens.
- `commonvp` and `get_cvp` return the common vnode shared by all snodes for the same block/character device.
- `sfind`, `sinsert`, and `sdelete` maintain the global `stable` hash table protected by `stable_lock`.
- `spec_assoc_vp_with_devi`, `spec_hold_devi_by_vp`, `devi_stillreferenced`, and `spec_devi_open_count` manage devinfo association, holds, and open/reference accounting.
- `spec_assoc_fence`, `spec_fence_snode`, and `spec_unfence_snode` set or clear `SFENCED` on common snodes when device instances are retired or restored.
- `common_specvp`, `specfind`, `spec_snode_walk`, `spec_is_clone`, `spec_is_selfclone`, and `spec_size_invalidate` provide lookup, iteration, clone-state, and cached-size invalidation helpers.
- `smark` updates snode access/modify/change timestamps and flags.
- `spec_maxoffset` computes maximum allowed offsets based on stream state and device 64-bit capability flags.
- `specinit` installs VFS/vnode ops, initializes locks, creates the snode kmem cache, initializes `spec_vfs`, and allocates a synthetic filesystem device id.
- `device_close` closes character or block devices, including stream close for character streams and block-cache invalidation on last close.
- `makectty` creates a character special vnode for a controlling terminal and increments the common snode open count.

## Concurrency and Lifetime
The global `stable_lock` protects the snode hash table. Each snode has `s_lock` and `s_cv` for per-snode state. Snode constructors allocate embedded vnodes and install specfs vnode ops. Shadow snodes hold their real vnode and VFS; common snodes are self-referential through `s_commonvp`. `spec_assoc_vp_with_devi` transfers devinfo holds from old to new associations and invalidates cached size when the associated device changes.

## Filesystem Relevance
Specfs is the VFS layer that represents character and block devices as vnodes. It bridges real filesystem device nodes, devfs-attached instances, common device identity, stream state, buffer-cache invalidation, page writeback, vnode path copying, and visibility checks for zones.

## Edge Cases and Risks
The common-vnode model is central: confusing shadow snodes with common snodes can corrupt open counts, device association, stream pointers, or cached size. `specvp` preallocates snodes before locking to avoid blocking under `stable_lock`; that pattern must be preserved. Devinfo fencing depends on retirement flags and common snode association. `spec_size_invalidate` obtains a held common snode through `sfind` and releases it asynchronously after clearing `SSIZEVALID`.
