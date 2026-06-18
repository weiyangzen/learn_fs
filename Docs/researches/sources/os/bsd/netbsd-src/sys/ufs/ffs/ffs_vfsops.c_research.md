# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vfsops.c

This file implements NetBSD FFS VFS operations: module registration, mount/update/reload/unmount, superblock validation, WAPBL replay/start integration, snapshot attachment, statvfs/sync, vnode initialization, NFS file handle conversion, pool lifecycle, and superblock/summary writeback.

Key responsibilities:
- Register FFS as a VFS module and define its `vfsops`.
- Mount root and regular FFS filesystems.
- Validate and load UFS1/UFS2/UFS2EA superblocks, including byte-swapped filesystems.
- Load summary information and initialize `ufsmount`.
- Handle read-only/read-write mount transitions, reloads, ACL flags, WAPBL, QUOTA2, snapshots, and discard.
- Flush, sync, and unmount filesystems.
- Allocate/load/reclaim inodes through vnode cache hooks.
- Write superblock and cylinder summary state.
- Convert between NFS file handles and vnodes.

Important functions:
- `ffs_checkrange`: Validates inode numbers for file handles, including UFS2 lazy-initialized inode range checks via cylinder group `cg_initediblk`.
- `ffs_snapshot_cb`: Kauth listener allowing snapshot creation by the file owner.
- `ffs_modcmd`: Attaches/detaches the FFS VFS and snapshot authorization listener.
- `ffs_mountroot`: Allocates and mounts the root FFS filesystem from `rootvp`.
- `ffs_acls`: Applies POSIX.1e/NFSv4 ACL mount/superblock flags, checks UFS2 EA support, and adjusts namecache/shared-lookup mount flags.
- `ffs_mount`: Main mount/update entry point. It validates device arguments and permissions, opens new mount devices, calls `ffs_mountfs`, handles r/w to r/o and r/o to r/w transitions, runs WAPBL replay/write/start/stop, reloads, starts QUOTA2, initializes discard, updates mount names, and writes dirty superblock state.
- `ffs_reload`: For read-only mounts after fsck, invalidates metadata, rereads the superblock and summaries, preserves in-memory pointer fields, reloads active inodes, and invalidates cached vnode data.
- `ffs_superblock_validate`: Sanitizes superblock size, block/fragment sizes, shift/mask consistency, inode-per-block counts, nonzero structural fields, frag count, and cylinder group size.
- `ffs_is_appleufs`: Detects Apple UFS through disk wedge type and optionally an Apple UFS label.
- `ffs_mountfs`: Common mount logic. It flushes device buffers, allocates `ufsmount`, initializes snapshots, searches superblock locations, handles UFS2EA magic and endian swapping, starts/replays WAPBL, loads summaries, initializes mount fields, attaches snapshots, starts WAPBL, mounts QUOTA2, and initializes discard.
- `ffs_oldfscompat_read` / `ffs_oldfscompat_write`: Translate old UFS1 superblock fields into modern in-memory fields and restore old layout fields before writeback.
- `ffs_unmount`: Flushes files, marks clean if appropriate, stops WAPBL/replay, closes the device, frees summaries/superblock/old compat state/snapshot state, and releases `ufsmount`.
- `ffs_flushfiles`: Stops quota/extattr state, flushes non-system vnodes, unmounts snapshots, flushes remaining vnodes and device metadata, and flushes WAPBL.
- `ffs_statvfs`: Fills block/inode counts, free/reserved/available counts, and statvfs metadata from FFS summaries.
- `ffs_sync`: Iterates dirty vnodes, updates inodes or fsyncs vnodes, syncs the device vnode, syncs quotas, writes modified superblock/summaries, and flushes WAPBL.
- `ffs_init_vnode` / `ffs_deinit_vnode`: Allocate/free in-core inode and dinode storage, load dinode data, initialize genfs node state, and attach/detach vnode data.
- `ffs_loadvnode`: Load an existing inode for vnode cache, reject unallocated inodes, set vnode ops, attach device vnode, set UVM size, and enter identity cache.
- `ffs_newvnode`: Allocate a new inode, initialize vnode/inode state, set uid/gid/mode/rdev/generation/birthtime, perform quota accounting, and publish vnode cache key.
- `ffs_fhtovp` / `ffs_vptofh`: Convert NFS `ufid` handles to/from vnodes with stale inode protection.
- `ffs_init`, `ffs_reinit`, `ffs_done`: Manage FFS inode/dinode pool caches and shared UFS init lifecycle.
- `ffs_sbupdate`: Writes the superblock, hiding internal flags, restoring old layout fields, converting UFS2EA magic, and byte-swapping if needed.
- `ffs_cgupdate`: Writes superblock plus cylinder summary blocks.
- `ffs_extattrctl`: Delegates UFS1 file-backed EA control to UFS extattr when available; otherwise uses standard extattr control.
- `ffs_vfs_fsync`: Fsyncs the mounted block device vnode, integrating WAPBL log flush and cache sync.

Important interactions:
- Integrates with `ffs_wapbl.c`, `ffs_snapshot.c`, `ffs_quota2.c`, `ffs_inode.c`, `ffs_subr.c`, shared UFS vnode/name/quota code, genfs, specfs, kauth, and NetBSD VFS.
- `ffs_mountfs` sets `mp->mnt_data`, `spec_node_setmountedfs`, `um_devvp`, `um_fs`, `um_ops`, and mount stat fields that most other FFS code relies on.
- Superblock/summary write paths use `ffs_getblk` and byte-swap helpers.

Notable behavior and risks:
- Dirty filesystem rejection logic is present but disabled with `#if 0`, matching comments about mount(8) behavior.
- WAPBL replay may force a superblock reread by jumping back to superblock search.
- UFS2EA on disk is normalized to UFS2 magic in memory with `UFS_EA` flag.
- Mount error cleanup must free several partially initialized structures; this path is careful but broad.
