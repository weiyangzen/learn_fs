# File Research: sources/os/linux/linux/fs/jfs/jfs_imap.c

## Role

Implements the JFS inode allocation map manager: mounting/syncing the inode map, reading/writing dinodes, allocating and freeing disk inodes and inode extents, maintaining IAG/AG free lists, and updating persistent inode bitmaps during transaction commit.

## Key Responsibilities

- Mounts the inode map in `diMount()` by reading the dinomap control page into an in-core `struct inomap` and initializing global/free-list locks.
- Unmounts and syncs the inode map through `diUnmount()` and `diSync()`, writing the dinomap control page, dirty imap pages, and the special imap inode.
- Reads regular inodes in `diRead()` by locating the containing IAG, validating the inode extent descriptor, handling legacy unaligned inode extents, reading the dinode page, checking inode number/link count, and copying dinode fields into the VFS inode.
- Reads/writes aggregate special inodes through `diReadSpecial()` and `diWriteSpecial()` from fixed AIT or secondary AIT locations.
- Writes regular dinodes in `diWrite()`, including inode base fields, inline symlink data, inline EA data, inline dtree root, regular-file xtree root, and directory-table xtree root.
- Frees disk inodes in `diFree()`, updating working maps, free-inode summary maps, per-IAG/per-AG/global counts, AG free-inode lists, AG free-extent lists, free-IAG lists, and freeing whole inode extents when above retention thresholds.
- Allocates disk inodes in `diAlloc()` using directory-vs-file policy: directories prefer `dbNextAG()`, files first try near the parent IAG unless the parent AG has active growing files.
- Allocates from the current AG with `diAllocAG()`, from any other AG with `diAllocAny()`, existing free backed inodes with `diAllocIno()`, or new inode extents with `diAllocExt()`.
- Performs low-level bit allocation in `diAllocBit()`, removing an IAG from the AG free-inode list when its last free inode is consumed.
- Initializes new inode extents in `diNewExt()`, allocating disk blocks, initializing every dinode in the extent, updating extent descriptors, working/persistent maps, summary maps, free lists, and counts.
- Allocates or reuses IAG pages in `diNewIAG()`, extending the inode map xtree when necessary and duplicating secondary AIT mapping state.
- Reads IAG pages with `diIAGRead()` and finds free bits with `diFindFree()`.
- Updates persistent inode allocation maps in `diUpdatePMap()` during transaction processing and links touched IAG metapages into log sync state.
- Rebuilds per-AG imap control lists after filesystem extension in `diExtendFS()`.
- Maintains the secondary aggregate inode table xtree through `duplicateIXtree()`, marking `JFS_BAD_SAIT` when it cannot be updated.
- Converts dinodes to in-core inode state in `copy_from_dinode()` and in-core inode state to dinodes in `copy_to_dinode()`.

## Important Interactions

- Uses IAG pages and dinomap structures defined in `jfs_imap.h`; uses filesystem geometry and fixed AIT offsets from `jfs_filsys.h`.
- Coordinates with the block allocator through `dbAlloc()`, `dbFree()`, `BLKTOAG()`, `AGTOBLK()`, `dbNextAG()`, and active AG counters.
- Coordinates with xtree code for inode-map and directory-table address trees.
- Uses metapage I/O for dinomap, IAG, and dinode pages.
- Uses transaction manager locks/commits for dinode writes, inode extent frees, imap xtree extension, persistent-map updates, and secondary AIT updates.
- Uses per-AG mutexes and an IAG free-list mutex for imap list serialization, plus `rdwrlock` on the imap inode for global map structure access.
- Uses quota-independent metadata inode handling for special inodes by setting `S_NOQUOTA`.
- Calls `check_dtroot()` when loading directory inodes to reject corrupt inline directory roots.

## Invariants and Risks

- Working maps (`wmap`) reflect currently allocated inodes; persistent maps (`pmap`) are updated during commit and must match transaction state.
- IAG free-inode and free-extent lists are doubly linked and require careful pre-reading of neighbor IAG pages to avoid partial updates and deadlocks.
- `im_agctl[].numfree` must never exceed `numinos`; multiple paths treat this as filesystem corruption.
- IAG page reads require the imap inode read lock except during quiesced extendfs processing.
- Whole inode extents are retained under low-water conditions to avoid excessive churn; otherwise they are freed and the IAG may return to the free-IAG list.
- `diNewIAG()` uses forced commits and synchronous writes so a newly appended IAG page and imap xtree remain recoverable.
- Special aggregate inodes bypass the normal inode map because they are needed early in mount.
- Legacy OS/2 unaligned inode extents require careful page/relative-inode calculation in both read and write paths.
- Dinode copying honors mount uid/gid/umask overrides while preserving saved on-disk uid/gid for later writeback.
