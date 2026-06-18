# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.c

## Purpose
Implements HAMMER2 ioctl dispatch and userland control operations for version queries, remote copy configuration, PFS scanning/creation/deletion/snapshotting, inode parameter access, bulkfree, emergency mode, destructive repair operations, growfs, and volume listing.

## Dispatch and Permissions
- `hammer2_ioctl()` begins with `caps_priv_check(cred, SYSCAP_NOVFS_IOCTL)` and selectively bypasses that result for non-privileged queries.
- Non-root allowed paths include version get, inode get, bulkfree scan in current code path, debug dump, and unsupported seek-hole/data handling depending on case logic.
- Mutating commands generally run only if the privilege check succeeded.
- `FIOSEEKDATA` and `FIOSEEKHOLE` return `EOPNOTSUPP`; disabled code references `vn_bmap_seekhole()`.

## Basic and Remote Operations
- `hammer2_ioctl_version_get()` returns media volume version from the first PFS device, or -1 if unavailable.
- `hammer2_ioctl_recluster()` takes a file descriptor, locates the PFS root cluster focus or sole chain, and reconnects the underlying device's KDMSG iocom.
- `hammer2_ioctl_remote_scan()` copies a selected `voldata.copyinfo` entry and computes the next occupied copyid.
- `hammer2_ioctl_remote_add()` allocates or uses a copyid, writes a copyinfo record into the volume header, marks voldata modified, and sends a volconf update.
- `hammer2_ioctl_remote_del()` deletes by copyid or by path search, clears the copyid field, and sends a volconf update.
- `hammer2_ioctl_remote_rep()` currently only locks/modifies voldata; replacement data is not copied into `copyinfo` in the visible implementation.
- Socket get/set are placeholders; get returns `EOPNOTSUPP`, set only validates copyid and locks/unlocks voldata.

## PFS Query Operations
- `hammer2_ioctl_pfs_get()` scans PFS entries under the media super-root, or returns the current file descriptor's mounted PFS when `name_key == -1`.
- It returns name key, PFS type/subtype, cluster ID, filesystem ID, name, and next key for iteration.
- `hammer2_ioctl_pfs_lookup()` hashes a supplied name, scans its collision range under the super-root, tests dirent names, and returns PFS identity fields.

## PFS Mutation
- `hammer2_ioctl_pfs_create()` validates name, checks for duplicates, starts a super-root flush transaction, creates a PFS inode, sets PFS metadata and default compression/check algorithms, disables compression for a PFS named `boot`, syncs/flushes the super-root inode, and allocates a local PFS association.
- `hammer2_ioctl_pfs_delete()` locates the PFS in the global PFS list for the target media, rejects mounted PFSs, deallocates the PFS cluster element, then permanently unlinks the PFS from the device super-root with force flags.
- `hammer2_ioctl_pfs_snapshot()` optionally syncs the source filesystem, sets `pfs_lsnap_tid`, creates a PFS inode under the super-root, assigns snapshot metadata and new UUIDs, copies the source root blockset from cached PFS root blocksets, flushes it, allocates a local PFS association, and seeds the snapshot inode allocator.

## Inode Ioctls
- `hammer2_ioctl_inode_get()` locks the inode shared, returns aggregate data/inode counts and the metadata portion of the inode.
- `hammer2_ioctl_inode_set()` starts a transaction, locks the inode, and conditionally updates check algorithm, compression algorithm, inode quota, data quota, and copy count before sideq transaction completion.

## Debug and Emergency Controls
- `hammer2_ioctl_debug_dump()` dumps each cluster chain through `hammer2_dump_chain()` with a high count limit.
- `hammer2_ioctl_emerg_mode()` toggles emergency flags on the PFS and all device mounts in its cluster, with console warnings.

## Bulkfree
- `hammer2_ioctl_bulkfree_scan()` serializes through `hmp->bflock`, syncs all mounted PFSs sharing the media, and chooses a snapshot topology unless ENOSPC forces live topology.
- Snapshot bulkfree runs outside a transaction; live bulkfree enters a flush transaction.
- It freezes the bulkfree thread, runs `hammer2_bulkfree_pass()`, unfreezes, drops the snapshot/live chain, converts HAMMER2 errors to errno, and releases the lock.
- As written, the dispatcher passes `NULL` for `HAMMER2IOC_BULKFREE_ASYNC`, but the function returns `EINVAL` on NULL data, so the async path is not actually asynchronous here.

## Destructive Repair
- `hammer2_ioctl_destroy()` rejects read-only PFSs.
- `HAMMER2_DELETE_FILE` force-unlinks a named directory entry under the fd directory with permanent/force/ignore-inode flags.
- `HAMMER2_DELETE_INUM` deletes a bad inode by inode number via the PFS root and `hammer2_delete_desc`.

## Growfs and Volumes
- `hammer2_ioctl_growfs()` supports only single-volume filesystems. It discovers device size from disklabel or vnode attributes, aligns to `HAMMER2_VOLUME_ALIGN`, rejects shrink and >2^63-1 sizes, clears newly exposed backup volume-header blocks, updates volume and allocator size/free counters in voldata and runtime structures, completes a flush transaction, and immediately syncs the filesystem.
- `hammer2_ioctl_volume_list()` copies out volume id, path, offset, and size for each volume up to caller capacity, then returns volume version and PFS name.

## Concurrency and Risk Notes
- Many operations lock `voldata` rather than chain topology to avoid deadlock with volume-chain locks.
- PFS deletion uses global `hammer2_mntlk` to coordinate with mount state.
- Snapshot creation serializes with `hmp->bulklk`.
- Remote replacement and socket operations are skeletal.
- Several control operations are marked with comments indicating incomplete clustering support, especially snapshots and growfs on multi-volume filesystems.
