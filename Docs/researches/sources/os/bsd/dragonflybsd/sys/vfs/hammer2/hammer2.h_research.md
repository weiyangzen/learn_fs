# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2.h

Central internal HAMMER2 kernel header defining in-memory topology, cluster state, transaction state, helper-thread state, XOP request structures, device/PFS structures, flags, inline helpers, global variables, and subsystem prototypes.

Key responsibilities:
- Defines lock and spinlock shims used by HAMMER2.
- Defines core in-memory chain topology structures for representing on-media objects, including chain cores, red-black child trees, blockref state, parent pointers, data buffers, and chain flags.
- Defines the HAMMER2 I/O cache wrapper around DragonFly buffers, including hash tables, reference/dirty/in-progress flags, dedup bitmaps, and debug tracking.
- Defines HAMMER2 error-code flags and conversion helpers between HAMMER2 internal errors and kernel `errno` values.
- Defines lookup, modify, resolve, delete, insert, flush, transaction, dirty-chain, logical-write, cluster, and thread flag sets.
- Defines cluster state for multi-node PFS operation, including quorum/synchronization flags and per-cluster chain items.
- Defines in-memory inode state, including locks, vnode association, embedded cluster, ccache, advisory-lock state, dirty/delete/create/sync flags, metadata copy, and size tracking.
- Defines PFS transaction counters and flags.
- Defines helper-thread structures used for synchronization, bulkfree, and XOP workers.
- Defines all XOP request payload structures and the `union hammer2_xop` used to fan out VOP work across cluster nodes.
- Defines device-vnode, volume, device, and PFS management structures.
- Declares global vop tables, tunables/stat counters, object caches, subsystem entry points, XOP descriptors, dmsg/rmsg handlers, I/O wrappers, chain/inode/cluster APIs, freemap APIs, vnode/VFS APIs, and admin-thread APIs.
- Provides inline helpers for dedup masks, error conversion, mount-to-PFS conversion, XOP focus-data access/release, and kqueue notification.

Important implementation details:
- HAMMER2's core object model is chain-based: volumes, inodes, indirect blocks, data blocks, and freemap nodes are represented by `hammer2_chain`.
- Chain block table updates are delayed for inserts/updates but performed immediately for deletions; flush code propagates modified chains bottom-up.
- Cluster operations use temporary working clusters, quorum checks, and XOP workers to avoid dead or stalled nodes blocking the frontend.
- XOP structures can reference up to four inodes and carry per-cluster FIFOs for pipelined backend responses.
- `hammer2_dev` represents a hard block device and can be shared by multiple mounted PFSs; `hammer2_pfs` represents a per-cluster filesystem view or the super-root.

Dependencies:
- Includes DragonFly kernel headers for vnode, mount, buffer cache, locks, threads, object cache, queues, red-black trees, namecache-adjacent structures, credentials, and dmsg.
- Includes HAMMER2 public/on-disk headers `hammer2_xxhash.h`, `hammer2_disk.h`, `hammer2_mount.h`, and `hammer2_ioctl.h`.
- Prototype declarations span nearly every HAMMER2 implementation file: subr, inode, chain, flush, ioctl, I/O, admin, XOP, synchronization, message, VFS, freemap, cluster, iocom, strategy, and ondisk.

Notable risks:
- This is a high-blast-radius internal ABI header; structural or flag changes affect most HAMMER2 compilation units.
- Concurrency semantics are encoded in comments, flags, and helper macros across chains, inodes, clusters, XOPs, and threads; changing them requires whole-filesystem reasoning.
- The cluster/quorum model permits partial availability and asynchronous backend completion, so error flag interpretation must remain consistent.
- `HAMMER2_INUMHASH_MASK` is defined from `HAMMER2_IOHASH_SIZE - 1`, which currently matches `HAMMER2_INUMHASH_SIZE` but is a latent coupling hazard if sizes diverge.
- Inline data access for XOP focus chains must be paired correctly with `hammer2_xop_pdata()` when `focus_dio` is referenced.
- Many subsystem interfaces accept locked structures or return locked/held references by convention, so misuse can cause leaks, deadlocks, or stale media-data access.
