# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_inode.c

## Purpose
Implements HAMMER2 in-memory inode lifecycle, locking, dependency grouping for sync, vnode association, inode creation, directory-entry creation, cluster repointing, unlink finalization, and synchronization of frontend inode state into backend chains.

## Inode Hashing and References
- `hammer2_inum_hash_init()` initializes per-PFS inode hash bucket spinlocks.
- `inumhash()` maps inode numbers to hash buckets.
- `hammer2_inode_lookup()` returns referenced in-memory inodes by inode number, except for super-root PFS contexts where duplicate inums prevent indexing.
- `hammer2_inode_ref()` increments refs and has optional debug tracing.
- `hammer2_inode_drop()` handles last-reference teardown: removes the inode from the hash, decrements PFS counts, clears cluster references via `hammer2_inode_repoint(ip, NULL)`, and frees the object.

## Locking and Sync Dependencies
- `hammer2_inode_lock()` supports shared and exclusive locks. Exclusive locks enforce SYNCQ semantics: if the inode is already staged for sync, it is moved to the front of the sync queue and the caller sleeps until safe.
- `hammer2_inode_lock4()` locks two to four inodes together, builds or merges dependency groups, and waits if any locked inode is on SYNCQ.
- `hammer2_inode_unlock()` wakes waiters marked by `HAMMER2_INODE_SYNCQ_WAKEUP` and drops the reference acquired by lock.
- Temporary release/restore and shared-to-exclusive upgrade/downgrade helpers wrap the inode mutex.
- `hammer2_inode_setdepend_locked()` is the core dependency merger. It handles SIDEQ, SYNCQ, PASS2, self-dependencies, dependency queue merging, and transaction rescan signaling.
- `hammer2_inode_depend()` groups two locked inodes so metadata dependencies such as directory entry and nlink updates are flushed together.
- `hammer2_inode_delayed_sideq()` places dirty inodes on the side queue lazily.

## Chain Access and Cluster Repointing
- `hammer2_inode_chain()` selects and locks a chain at a cluster index.
- `hammer2_inode_chain_and_parent()` obtains child and parent in lock order, retrying if the relationship changes.
- `hammer2_inode_repoint()` replaces all chains in an inode's embedded cluster, drops cached data chains, updates focus and flags, and drops old chain refs after releasing the spinlock.
- `hammer2_inode_repoint_one()` updates one cluster element, used by synchronization threads for piecemeal cluster updates.
- `hammer2_inode_data_count()` and `hammer2_inode_inode_count()` report maximum aggregate stats across cluster chains.

## Vnode Integration
- `hammer2_igetv()` returns an exclusively locked vnode for an inode, reusing an existing vnode when possible while dropping the inode lock around `vget()` to avoid reclaim deadlocks.
- It allocates new vnodes with type-specific setup:
  - Directories become `VDIR`.
  - Regular files and symlinks use VKVABIO and VMIO initialized to logical buffer size.
  - Character/block devices use spec ops and aliases.
  - FIFOs use fifo ops.
  - Sockets become `VSOCK`.
- The PFS root vnode is marked `VROOT`.

## Inode Creation
- `hammer2_inode_get()` returns an existing or new in-memory inode synchronized to an XOP cluster. It handles insertion races into the inode hash and can create super-root/PFS-style unindexed inodes.
- `hammer2_inode_create_pfs()` creates a PFS inode under the super-root inside a flush transaction. It computes a directory hash key, scans for collision-free low hash bits, builds metadata, creates the media chain through XOPs, and returns the locked inode.
- `hammer2_inode_create_normal()` creates regular inodes in memory and detached backend chains during a normal transaction. It sets metadata from parent/vattr/credentials, handles device numbers and uid/gid inheritance, enables direct data for regular files and symlinks, and marks the inode `HAMMER2_INODE_CREATING` for later insertion.
- `hammer2_dirent_create()` creates a directory entry under a locked directory, resolving name-hash collisions and issuing a mkdirent XOP.

## Unlink and Deletion
- `hammer2_inode_unlink_finisher()` decrements `nlinks`, marks zero-link inodes as unlinked, queues vnode recycling when possible, and queues no-vnode inodes for deletion.
- `hammer2_inode_vprecycle()` aggressively finalizes a vnode after unlink to allow reclaim of zero-link inodes.
- `hammer2_inode_chain_des()` turns `HAMMER2_INODE_DELETING` into a backend destroy XOP and clears both deleting and unlinked flags.

## Inode Sync
- `hammer2_inode_modify()` marks in-memory metadata dirty, marks an associated vnode dirty, and queues the inode unless `NOSIDEQ` is set.
- `hammer2_inode_chain_sync()` pushes in-memory metadata and resize state to backend chains. It clears direct-data mode when size exceeds embedded capacity and starts an fsync XOP.
- `hammer2_inode_chain_ins()` inserts newly created detached inode chains into the media topology during sync.
- `hammer2_inode_chain_flush()` clears `DIRTYDATA`, starts the inode flush XOP, waits for all cluster elements, and treats ENOENT as success.

## Concurrency and Edge Cases
- The code intentionally separates inode locks from chain locks to avoid confusing multi-holder inode state and chain lifecycle.
- SYNCQ/PASS2 logic is designed to prevent crash-inconsistent splits between related inode updates.
- Super-root PFS contexts are special because inode number uniqueness is not guaranteed.
- `hammer2_inode_get()` temporarily unholds XOP clusters to avoid deadlocks against vnode recycling.
- Creation APIs distinguish PFS creation, which inserts directly into the super-root during a flush transaction, from normal inode creation, which defers media topology insertion.
