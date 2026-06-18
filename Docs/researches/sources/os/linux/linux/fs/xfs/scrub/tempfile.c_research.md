# File Research: sources/os/linux/linux/fs/xfs/scrub/tempfile.c

This file implements hidden temporary inodes and atomic content exchange support for online repair. Repairs rebuild file-based metadata in an unlinkable private inode, then exchange fork mappings with the damaged metadata inode.

Major entry points:
- `xrep_tempfile_create`: creates an unlinkable private tempfile of a requested mode.
- `xrep_tempfile_rele`: releases and cleans up `sc->tempip`.
- `xrep_tempfile_adjust_directory_tree`: converts temp regular/dir files into metadata-directory files when repairing metadata-directory inodes.
- Tempfile lock helpers: IOLOCK/ILOCK nowait, polled, lock, unlock, both-inode lock/unlock.
- `xrep_tempfile_prealloc`: ensures a tempfile range has written extents.
- `xrep_tempfile_copyin`: writes block data to preallocated tempfile extents through a callback.
- `xrep_tempfile_set_isize`: updates disk and VFS inode size.
- `xrep_tempfile_roll_trans`: logs tempfile core and rolls repair transaction.
- `xrep_tempexch_trans_reserve`, `xrep_tempexch_trans_alloc`, `xrep_tempexch_contents`: exchange-map transaction support.
- `xrep_tempfile_copyout_local`: direct local fork copy for shortform forks.
- `xrep_is_tempfile`: identifies repair tempfiles.

Tempfile creation:
- Uses root inode as parent context and `XFS_ICREATE_TMPFILE | XFS_ICREATE_UNLINKABLE`.
- Allocates root-owned dquots so quota limits do not block repair.
- Drops realtime inheritance flags because tempfiles are metadata staging objects.
- Marks VFS inode `S_PRIVATE` and clears `IOP_XATTR` so LSM/ACL/xattr layers ignore it.
- Initializes directories with `xfs_dir_init`.
- Initializes symlinks with a harmless one-byte target.
- Places the inode on the unlinked list so recovery/inactivation purges it if repair aborts.

Metadata-directory handling:
- Since tempfiles are created before scrub knows if `sc->ip` is a metadir inode, `xrep_tempfile_adjust_directory_tree` later marks eligible temp dir/reg files as metadata files, subtracting quota inode count and detaching dquots.
- `xrep_tempfile_remove_metadir` reverses that before normal inactivation.

Preallocation/copy-in:
- `xrep_tempfile_prealloc` walks mappings, rejects delalloc, converts holes/unwritten extents into written zeroed extents, and finishes deferred work.
- `xrep_tempfile_copyin` reads each mapping, gets the metadata buffer at the mapped disk address, invokes a caller callback to populate/verify it, queues delayed writes, and flushes every 512 KiB.

Exchange support:
- `xrep_tempexch_prep_request` fills `xfs_exchmaps_req`.
- `xrep_tempexch_estimate` handles local-format forks by estimating required local-to-extent conversion overhead.
- `xrep_tempexch_reserve_quota` reserves quota when exchanging blocks between inodes with distinct dquots.
- `xrep_tempexch_trans_reserve` is for callers that already hold dirty locked inodes.
- `xrep_tempexch_trans_alloc` creates a new truncate-style transaction and uses exchange-range locking.
- `xrep_tempexch_contents` calls `xfs_exchange_mappings`, finishes deferred work, and swaps incore VFS sizes when `XFS_EXCHMAPS_SET_SIZES` is set.

Risk notes:
- Locking is deliberately try/poll based in places to avoid deadlocks while another inode lock is held.
- `xrep_is_tempfile` must distinguish repair tempfiles from metadata-directory files that also use private flags; it uses `XFS_IRECOVERY` for temporary metadir inodes.
- The exchange path rejects COW fork exchange because COW forks do not exist on disk.
