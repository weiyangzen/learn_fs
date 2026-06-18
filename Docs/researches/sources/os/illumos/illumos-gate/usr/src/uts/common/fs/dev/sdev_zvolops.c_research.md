# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_zvolops.c

This file implements dynamic vnode operations for `/dev/zvol`, including `/dev/zvol/dsk` and `/dev/zvol/rdsk`. It bridges sdev with ZFS zvol discovery, zvol minor creation, global-zone symlink generation, and non-global-zone direct device-node creation.

Core responsibilities:
- Defines `devzvol_vnodeops_tbl`, overriding lookup, readdir, create, and rejecting namespace mutations.
- Dynamically opens `fs/zfs` and `/dev/zfs` instead of statically linking sdev to ZFS.
- Resolves `zvol_create_minor` and `zvol_name2minor` using `ddi_modsym`.
- Uses ZFS ioctls to test datasets, list pools/datasets/snapshots, and cache pool configuration data.
- Builds `/dev/zvol` hierarchy entries from ZFS object-set state.
- Handles the global-zone and non-global-zone zvol namespace differences.

Important operations:
- `sdev_zvol_create_minor` and `sdev_zvol_name2minor` wrap dynamically resolved ZFS symbols.
- `devzvol_open_zfs` opens `/dev/zfs`, modopens `fs/zfs`, resolves required zvol symbols, and records the zfs device major.
- `devzvol_close_zfs` releases the LDI handle, ident, module handle, and function pointers.
- `devzvol_handle_ioctl` serializes most ZFS ioctls through `devzvol_mtx`, grows nvlist destination buffers on `ENOMEM`, and lazily opens ZFS.
- `devzvol_objset_check` uses `ZFS_IOC_POOL_STATS` or `ZFS_IOC_OBJSET_STATS` and returns the object-set type. Snapshot visibility is controlled by `devzvol_snaps_allowed`.
- `devzvol_make_dsname` maps `/dev/zvol/{dsk,rdsk}/...` paths plus optional names to ZFS dataset names.
- `devzvol_validate` checks whether cached sdev nodes are still valid. It detects deleted datasets, stale type transitions, stale zvol-minor symlinks, and special non-global-zone profile pass-through cases.
- `devzvol_update_zclist` and `devzvol_update_zclist_cb` maintain a cached pool-config nvlist via taskq so pool listing runs in a safe global context.
- `devzvol_create_pool_dirs` creates pool directories under `/dev/zvol/dsk` and `/dev/zvol/rdsk`.
- `devzvol_create_dir` creates directory vattrs for pools or datasets.
- `devzvol_create_link` creates global-zone zvol symlinks pointing into `ZVOL_PSEUDO_DEV`, with raw-device suffix handling for `rdsk`.
- `devzvol_prunedir` validates and removes obsolete cached entries before directory enumeration.
- `devzvol_mk_ngz_node` creates non-global-zone zvol nodes directly as VBLK/VCHR devices because zones do not have a usable `/devices` target for global-style symlinks.
- `devzvol_lookup` enforces the global-zone versus non-global-zone lookup split. It prevents global-zone traversal into a zone’s `/dev/zvol`, avoids creating nonsensical profile shadows from NGZ context, and creates either directories or links based on object-set type.
- `sdev_iter_datasets` and `sdev_iter_snapshots` populate cached children through ZFS list ioctls.
- `devzvol_readdir` creates `dsk`/`rdsk`, pool directories, dataset directories, and optional snapshot entries as needed.

Mutation policy:
- `devzvol_create` only opens existing entries; absent names map to `EROFS`.
- Rename, mkdir, rmdir, remove, and symlink are `fs_nosys`.

Security and namespace notes:
- Global-zone zvol entries are symlinks to pseudo-device nodes.
- Non-global-zone zvol entries may be direct block/character device nodes when datasets are delegated or explicitly profile-matched.
- The code explicitly blocks global-zone lookup into a non-global-zone `/dev/zvol` to avoid materializing all zone zvol devices and crossing delegation boundaries.

Research notes:
- This is the key file for zvol `/dev` materialization and stale zvol cleanup.
- The ZFS coupling is intentionally late-bound through `ddi_modopen`, LDI, and ioctl calls.
- Important concurrency state is protected by `devzvol_mtx`, especially ZFS open state and cached pool configuration state.
