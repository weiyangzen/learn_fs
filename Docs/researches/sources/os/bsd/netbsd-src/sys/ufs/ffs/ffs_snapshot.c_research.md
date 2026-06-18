# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_snapshot.c

This file implements FFS filesystem snapshots and snapshot copy-on-write. It tracks active snapshot inodes, creates persistent snapshot files, excludes unwanted live state from snapshot images, intercepts block writes/frees, and reattaches snapshots at mount.

Key responsibilities:
- Maintain per-mount snapshot state and active snapshot lists.
- Create a snapshot file with preallocated metadata coverage.
- Copy cylinder groups, superblock, and summary data into the snapshot.
- Expunge unlinked files and older snapshots from the snapshot view.
- Provide block-level copy-on-write before live filesystem writes overwrite data needed by snapshots.
- Claim or copy blocks that are being freed while snapshots still need their old contents.
- Reattach snapshot inodes on mount and detach them on unmount.
- Provide snapshot reads over filesystem-size logical space.

Important functions:
- `ffs_snapshot_init` / `ffs_snapshot_fini`: Allocate and destroy `snap_info`, locks, active snapshot list, generation counter, and block hint list.
- `ffs_snapshot`: Main creation flow. It checks for an existing snapshot and free `fs_snapinum` slot, prepares the vnode, copies cylinder groups, marks the snapshot valid, fsyncs, suspends the filesystem, recopies changed cylinder groups, copies superblock/summary data, expunges unlinked files, registers the snapshot, establishes COW for the first snapshot, expunges snapshot blocks, writes snapshot metadata, flushes pages, and handles cleanup on error.
- `snapshot_setup`: Verifies mount/permissions/writecount, truncates the file, marks it `SF_SNAPSHOT|SF_SNAPINVAL`, writes a block-hint-list size placeholder, and preallocates indirect blocks, superblock, summary blocks, and cylinder group blocks.
- `snapshot_copyfs`: Creates an in-memory copy of the superblock and cylinder summaries, initializes maxcluster data, and clears `FS_DOWAPBL` in the snapshot copy.
- `snapshot_expunge`: Finds unlinked active vnodes and the in-filesystem WAPBL log, removes their blocks from the snapshot view, frees their copied inode state, and creates a preliminary list of preallocated snapshot blocks.
- `snapshot_expunge_snap`: Accounts older snapshots into the new one, removes invalid/unlinked snapshot inodes from the copied view, builds `i_snapblklist`, and writes that list to the end of the snapshot.
- `snapshot_writefs`: Writes copied summaries and superblock into the snapshot and ensures direct blocks needed by COW/snapblkfree are copied.
- `cgaccount` / `cgaccount1`: Copy cylinder group maps into the snapshot and mark free blocks as `BLK_NOCOPY`.
- `expunge` / `indiracct`: Rewrite the copied inode image for an expunged inode and walk direct/indirect block maps for accounting callbacks.
- `snapacct`, `mapacct`, `fullacct`: Mark snapshot-owned blocks and remove blocks from copied allocation maps.
- `ffs_snapgone`: Removes a deleted snapshot inode from `fs_snapinum` and drops the extra active reference.
- `ffs_snapremove`: Removes a snapshot from active COW tracking, clears COW if it was last, releases its hint list, clears `BLK_NOCOPY`/`BLK_SNAP` markers, and converts it back to a normal inode.
- `ffs_snapblkfree`: Handles block-free notifications. It lets snapshots claim full blocks directly or copies fragment/full-block data before allowing the free.
- `ffs_snapshot_mount`: Reads `fs_snapinum[]`, validates snapshot inodes, reads their block hint lists, links them onto the active list, and establishes COW.
- `ffs_snapshot_unmount`: Removes active snapshots, frees hint lists, drops references, and disestablishes COW.
- `ffs_copyonwrite`: COW callback for writes. It skips blocks outside the filesystem, in the journal, or in the precomputed no-copy list; otherwise it copies old block contents into snapshots that still map the block.
- `ffs_snapshot_read`: Reads snapshot logical data, optionally over the snapshot file size with `IO_ALTSEMANTICS`.
- `snapblkaddr`, `rwfsblk`, `syncsnap`, `wrsnapblk`: Lookup and raw read/write helpers for snapshot block handling.
- `db_get`, `db_assign`, `ib_get`, `idb_get`, `idb_assign`: UFS1/UFS2 and endian-aware block pointer helpers.

Important interactions:
- Uses `fscow_establish`/`fscow_disestablish` for copy-on-write integration.
- Works closely with `ffs_balloc`, `ffs_blkfree_snap`, `ffs_freefile_snap`, `ffs_truncate`, WAPBL, UVM, buffer cache, and quota hooks.
- Persistent snapshot state is recorded in `fs_snapinum[]` and per-snapshot block hint lists stored at the end of the snapshot file.

Notable behavior and risks:
- Snapshot creation briefly suspends the filesystem after most allocation is done to minimize suspension time.
- `si_gen` protects against snapshot list changes while locks are dropped.
- COW avoids the in-filesystem journal range to prevent WAPBL deadlocks/recursion.
- If copying a fragment during free fails, `ffs_snapblkfree` can deny the free to preserve snapshot consistency at the cost of leaked space.
- Snapshot support can be compiled out with `FFS_NO_SNAPSHOT`, leaving `ffs_snapshot` as `EOPNOTSUPP`.
