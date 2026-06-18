# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_imap.c

This file implements the JFS inode allocation map manager. It mounts and syncs inode map metadata, reads and writes dinodes, allocates and frees inode numbers and inode extents, manages inode allocation group lists, updates persistent allocation maps during commit, handles filesystem extension, and maintains the secondary aggregate inode table.

Key responsibilities:
- Mounts the inode map in `diMount()` by reading the on-disk dinomap control page into an in-memory `struct inomap`, converting per-AG counters and initializing locks.
- Syncs and unmounts the inode map through `diSync()` and `diUnmount()`, writing control-page state and flushing dirty inode-map pages.
- Reads regular dinodes in `diRead()` by locating the target IAG, resolving the inode extent, handling OS/2-era unaligned inode extents, reading the containing page, and copying the dinode into the VFS inode.
- Reads and writes aggregate special inodes through `diReadSpecial()` and `diWriteSpecial()` using fixed aggregate inode table locations or the secondary AIT.
- Writes regular dinodes in `diWrite()`, copying base inode fields plus inline symlinks, inline EAs, inline directory roots, directory-index xtree roots, or regular-file xtree roots under transaction line locks.
- Frees inodes in `diFree()`, updating the working map, summary maps, per-IAG counters, per-AG free-inode/free-extent lists, global counters, quota-visible extent ownership, and logging freed inode extents when an entire inode extent is released.
- Allocates inodes in `diAlloc()`, preferring parent locality for files, allocation-group rotation for directories, and avoiding active AGs used by growing regular files.
- Allocates from a specific AG or any AG through `diAllocAG()`, `diAllocAny()`, and `diAllocIno()`.
- Allocates backed inode extents through `diAllocExt()` and initializes new inode extents through `diNewExt()`, including disk inode initialization, free-list maintenance, and block allocation.
- Allocates or extends IAG pages through `diNewIAG()`, including transactionally extending the inode-map xtree, synchronously initializing the new page, adding it to the free-IAG list, and duplicating the xtree into the secondary AIT when possible.
- Updates the persistent inode map in `diUpdatePMap()` during transaction commit and attaches the IAG metapage to log sync state.
- Rebuilds per-AG inode-map lists after filesystem growth in `diExtendFS()`.
- Converts between dinode and in-memory inode fields in `copy_from_dinode()` and `copy_to_dinode()`, including mount uid/gid/umask overrides, timestamps, device numbers, ACL/EA descriptors, directory dtree roots, and xtree roots.

Important interactions:
- Uses `struct inomap`, `struct iag`, and dinomap formats from `jfs_imap.h`.
- Coordinates with the block allocator for inode extent and IAG-page allocation/free.
- Coordinates with xtree code for inode-map addressability and with the transaction manager for inode, map, and freed-extent logging.
- Uses JFS private inode fields from `jfs_incore.h`, especially `ixpxd`, `agstart`, `ipimap`, inline roots, commit flags, and transaction lock IDs.
- Uses metapage I/O for inode map pages and raw/special aggregate inode table pages.
- Integrates with quota by marking metadata inodes `S_NOQUOTA`; actual user inode quota charging is handled around `ialloc()` and VFS inode lifecycle.

Notable invariants and risks:
- Lock ordering is explicit: AG list locks protect per-AG lists, IAG pages are locked by holding metapages, and the inode-map inode read/write lock protects global map state and IAG addressability.
- Working maps (`wmap`) track current allocation, while persistent maps (`pmap`) are updated through commit; the two must transition in the expected order.
- Summary maps use inverted availability semantics in places: set bits can mean no backed free inodes, while clear bits identify candidate free resources.
- Freeing an inode may free an entire inode extent only above low-water thresholds; otherwise the extent is retained to avoid churn.
- Careful update paths read all IAGs that will be linked/unlinked before mutating list pointers to avoid partially updated free lists.
- New IAG creation must keep the inode map, control page, and secondary AIT synchronized enough for recovery; failure paths mark `JFS_BAD_SAIT` when the secondary copy cannot be maintained.
- Dinode page addressing handles unaligned inode extents from OS/2-created filesystems, so page and relative-inode calculations are more complex than a simple division.
- `copy_from_dinode()` validates directory roots with `check_dtroot()` before exposing directory state to the rest of JFS.

Research notes:
- This is the allocator and serialization center for JFS inode metadata. The critical concepts are IAGs, backed inode extents, per-AG free lists, the split between working and persistent bitmaps, and transaction-time synchronization with log recovery.
