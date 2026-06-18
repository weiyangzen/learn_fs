# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_xops.c

HAMMER2 per-node backend XOP implementation. These routines execute VFS/inode operations against one cluster element’s chain topology and feed locked chain results or completion status back to the frontend XOP collector.

Key responsibilities:
- Implements backend operations for inode cluster lookup, readdir, name resolve, unlink/rmdir/PFS delete, rename, collision-space scans, key lookup/delete, full scans, inode create/connect/destroy/unlinkall, inode-chain sync, and bmap.
- Provides `checkdirempty()` to validate directory emptiness while handling both embedded inode chains and separate dirent chains.
- Drives namespace scans over HAMMER2 directory hash ranges and exact key ranges.
- Creates inline or external-buffer directory entries depending on name length.
- Creates normal attached inodes, detached inodes, and inserts detached inodes into the topology.
- Deletes chains permanently or logically depending on operation flags.
- Syncs frontend inode metadata into backend inode chains and removes data chains beyond new EOF for truncation.
- Resolves logical offsets to physical `data_off` values for bmap.

Important implementation details:
- Backend functions typically acquire a chain for `head.ip1` at `clindex` with either shared or exclusive resolve flags, perform lookup/create/delete work, then call `hammer2_xop_feed()`.
- Fed chains are generally locked when transferred to the frontend; callers then unlock/drop local references after feeding according to XOP conventions.
- `checkdirempty()` may unlock and relock caller-supplied chains to find the real inode behind a dirent; it returns `HAMMER2_ERROR_EAGAIN` if topology changed and the caller must retry.
- Name resolution hashes the requested name, scans the collision range, tests candidate dirents, and resolves separate dirent records to inode chains by inode number.
- Unlink/rmdir validate type expectations, directory emptiness, forced/permanent-delete flags, and can return the target inode chain for frontend nlink/disposition finishing.
- Rename handles embedded inodes and separate dirents, deletes the old entry, updates stored filename/name-key/iparent metadata for crash/debug consistency, deletes duplicate target entries as self-healing, then inserts the renamed chain into the target directory.
- `hammer2_xop_inode_chain_sync()` handles truncation by deleting data chains above rounded-up EOF before copying updated inode metadata into the inode chain.

Dependencies:
- Includes `hammer2.h` and relies on HAMMER2 chain lookup, create, delete, resize, modify, parent lookup, inode-chain acquisition, inode-number lookup, dirent comparison, XOP feed, and error-code conventions.
- Called by frontend VOP/inode/admin code via XOP descriptors declared elsewhere, especially from `hammer2_vnops.c`, inode creation/deletion paths, sync paths, and bmap/strategy paths.

Notable risks:
- Topology mutation is concurrency-sensitive; several operations intentionally drop and reacquire locks, so `EAGAIN` retry handling is required for correctness.
- Frontend/backend split means backend chains and frontend `hammer2_inode_t` metadata can be temporarily unsynchronized; comments explicitly assign final nlink and metadata authority to frontend code in several paths.
- Rename is complex and mixes deletion, metadata rewrite, duplicate-target cleanup, and reinsertion; partial errors can leave work for recovery/self-healing.
- Directory emptiness checks for rename/unlink depend on exact visible namespace ranges and correct handling of dirent-vs-inode representations.
- Several paths use assertions or debugging prints for states considered impossible but observed under stress, indicating fragile historical edge cases.
