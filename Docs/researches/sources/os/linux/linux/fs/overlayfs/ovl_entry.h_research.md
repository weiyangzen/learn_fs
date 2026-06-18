# File Research: sources/os/linux/linux/fs/overlayfs/ovl_entry.h

## Purpose

`ovl_entry.h` defines overlayfs private mount, layer, dentry, and inode state. It is the core data model used by lookup, readdir, copy-up, inode operations, xattrs, export, and superblock setup.

## Key Structures

`struct ovl_config` stores effective mount configuration: `upperdir`, `workdir`, lower directory strings, default permissions, redirect mode, verity mode, index, UUID mode, NFS export, xino, metacopy, userxattr, and fsync mode.

`struct ovl_sb` represents a unique underlying superblock. It tracks the real superblock, overlay pseudo device number, whether UUID identity is unusable due to conflicts, and whether the filesystem is used as a lower layer.

`struct ovl_layer` represents one layer. Layer index 0 is reserved for upper. Each layer stores its private mount, trap inode, underlying `ovl_sb`, stack index, fsid, and xwhiteout marker state.

`struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is attached to overlay inodes and contains the counted lower stack.

`struct ovl_fs` is the overlay superblock-private state. It owns layer arrays, unique filesystem records, work/index directories, config strings, creator credentials, feature fallback flags, in-use locks, xino mode, whiteout cache, volatile errseq state, and casefold state.

`struct ovl_inode` wraps a VFS inode. It stores a directory cache or lowerdata redirect, redirect string, version counter, overlay flags, upper dentry, lower entry, and a mutex for copy-up and related transitions.

## Important Inline Helpers

- `ovl_numlowerlayer()` excludes upper and data-only lower layers from the normal lower-layer count.
- `ovl_upper_mnt()` and `ovl_upper_mnt_idmap()` access the upper mount and idmap.
- `OVL_FS()`, `OVL_I()`, `OVL_E()`, and `OVL_I_E()` cast VFS objects to overlay-private state.
- `ovl_numlower()`, `ovl_lowerstack()`, `ovl_lowerpath()`, and `ovl_lowerdata()` access lower-stack entries.
- `ovl_lowerdata_dentry()` reads lazy lowerdata dentries with `READ_ONCE()`.
- `OVL_E_FLAGS()` stores dentry-private flags in `d_fsdata`.
- `ovl_upperdentry_dereference()` reads the upper dentry with `READ_ONCE()`.

## Invariants

- `ofs->layers[0]` is the upper layer slot, even for lower-only overlays.
- Normal lower layers start at index 1.
- Data-only lower layers are included in `numlayer` but excluded from the normal merged lower count.
- `struct ovl_entry` lowerstack entries are ordered from top to bottom.
- The last lowerstack entry may represent lowerdata, and may initially have no dentry when lazy lookup is needed.
- Directory inodes use `ovl_inode.cache`; regular files may use `ovl_inode.lowerdata_redirect`.
- Dentry flags live in `d_fsdata`; inode flags live in `OVL_I(inode)->flags`.

## Integration

`params.c` fills `ovl_config` and `ovl_fs_context`. `super.c` converts parsed paths into `ovl_layer`, `ovl_sb`, and root `ovl_entry` state. `namei.c` builds per-dentry lower stacks. `readdir.c` stores merged directory caches in `ovl_inode.cache`. `util.c` reads and mutates most of the state defined here.

## Risk Notes

- The `ovl_inode` union is mode-dependent; directory and regular-file paths must use the correct member.
- Lazy lowerdata publication depends on memory ordering with `READ_ONCE()` and barriers in `util.c`.
- Layer numbering, fsid numbering, and data-only layer exclusion are easy sources of off-by-one errors.
