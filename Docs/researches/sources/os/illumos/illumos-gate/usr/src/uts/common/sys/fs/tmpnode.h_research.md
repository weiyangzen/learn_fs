# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmpnode.h

## Role

Defines the tmpfs filesystem-dependent node structures used by illumos tmpfs. `struct tmpnode` is the in-core representation behind tmpfs vnodes, covering directories, symlinks, regular-file anonymous backing storage, attributes, locks, extended-attribute directories, and tmpfs-specific flags.

## Key Interfaces

- `struct tmpnode` stores linked-list membership, a vnode backpointer, pseudo generation number, `struct vattr`, and a tagged union for directory entries, symlink text, or anon backing.
- Field aliases expose vnode attributes as `tn_mode`, `tn_uid`, `tn_size`, timestamps, block counts, and sequence number.
- `struct tdirent` represents tmpfs directory entries with bidirectional list links, per-directory parent pointer, hash link, name, offset, and target tmpnode.
- `struct tfid` overlays `fid` for VFS `VGET`.
- Exports `tmp_vnodeops` and `tmp_vnodeops_template`.

## Locking and Integration Notes

The file documents tmpfs lock ordering: `tn_rwlock -> tn_contents -> page locks`. `tn_tlock` is independent for mode, nlink, time, and flag updates. Directory lists and file growth/truncation depend on the documented interaction between `tn_rwlock`, `tn_contents`, and anon-array updates.

## Risk Notes

Changes here affect tmpfs vnode state, directory traversal, anonymous memory backing, and xattr behavior. The union-backed layout requires consumers to interpret fields only according to vnode type.
