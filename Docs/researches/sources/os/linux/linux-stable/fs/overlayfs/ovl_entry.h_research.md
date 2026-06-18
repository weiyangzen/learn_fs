# File Research: sources/os/linux/linux-stable/fs/overlayfs/ovl_entry.h

## Purpose

`ovl_entry.h` defines overlayfs private mount, layer, dentry, and inode state structures. It is the data model used by the rest of overlayfs.

## Key Structures

`struct ovl_config` stores user-visible and effective mount configuration:

- `upperdir`, `workdir`, and `lowerdirs`
- `default_permissions`
- redirect, verity, index, UUID, NFS export, xino, metacopy, userxattr, and fsync modes

`struct ovl_sb` tracks each unique underlying superblock, its pseudo device number, UUID conflict state, and whether it is used as a lower layer.

`struct ovl_layer` represents one overlay layer. Layer index 0 is reserved for upper. Each layer stores a private mount, trap inode, underlying `ovl_sb`, stack index, fsid, and xwhiteout marker state.

`struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is attached to overlay inodes and contains the counted lower stack.

`struct ovl_fs` is overlay superblock private state. It owns layer arrays, unique fs records, work/index dirs, config strings, creator credentials, feature fallbacks, in-use locks, xino mode, whiteout cache, volatile errseq, and casefold state.

`struct ovl_inode` wraps a VFS inode and stores directory cache or lowerdata redirect, redirect string, version, overlay flags, upper dentry, lower entry, and a mutex for copy-up and related transitions.

## Important Inline Helpers

- `ovl_numlowerlayer()` excludes upper and data-only layers.
- `ovl_upper_mnt()` and `ovl_upper_mnt_idmap()` access upper layer mount/idmap.
- `OVL_FS()`, `OVL_I()`, `OVL_E()`, and `OVL_I_E()` cast VFS objects to overlay-private state.
- `ovl_lowerstack()`, `ovl_lowerpath()`, and `ovl_lowerdata()` access lower stack entries.
- `ovl_lowerdata_dentry()` allows lazy lowerdata entries to be absent.
- `OVL_E_FLAGS()` stores dentry-private flags in `d_fsdata`.
- `ovl_upperdentry_dereference()` reads the upper dentry through `READ_ONCE()`.

## Invariants

- `ofs->layers[0]` is upper when present; lower layers start at index 1.
- Data-only lower layers are part of `numlayer` but excluded from normal merged lower count.
- `struct ovl_entry` lowerstack order is top-to-bottom for merge lookup; its last entry can represent lowerdata.
- Directory inodes use `ovl_inode.cache`; regular files may use `ovl_inode.lowerdata_redirect`.
- Dentry flags live in `d_fsdata`, while inode flags live in `OVL_I(inode)->flags`.

## Integration

Every file in this group relies on these structures. `params.c` fills config and fs-context state; `super.c` builds `ovl_fs`, layers, and root `ovl_entry`; `namei.c` creates per-dentry lower stacks; `readdir.c` caches merged directory entries in `ovl_inode.cache`; `util.c` reads and mutates most of the private state.

## Risk Notes

- The union in `ovl_inode` is type-dependent; directory and regular-file paths must not use the wrong member.
- Lazy lowerdata uses memory-ordering assumptions around the lowerdata `ovl_path`.
- Layer numbering and data-only layer accounting are easy sources of off-by-one errors.
