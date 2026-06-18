# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer.h

This is HAMMER’s central internal kernel header. It defines the in-memory structures, flags, helper inlines, global tunables/statistics, and cross-module function prototypes used by the HAMMER filesystem implementation. On-disk formats are delegated to `hammer_disk.h`, while this file models runtime state and internal APIs.

Major data structures:
- `hammer_transaction`: transaction state, TID, timestamp fields, sync-lock refs, flags, and root volume.
- `hammer_lock`: HAMMER’s custom ref/lock structure with reference flags, exclusive lock bits, owner tracking, and inline state tests.
- `hammer_pseudofs_inmem`: in-memory pseudo-filesystem metadata and locking.
- `hammer_objid_cache`: directory-local object-id allocation cache for locality.
- `hammer_node_cache`: cached B-Tree node search-start association.
- `hammer_flush_group`: chunked inode flush grouping to avoid exhausting the UNDO FIFO during large syncs.
- `hammer_inode`: core in-memory inode object, including RB-tree linkage, vnode pointer, pseudofs pointer, inode data cache, record tree, flush/sync copies, dirty flags, REDO tracking, and B-Tree node caches.
- `hammer_record`: unsynchronized in-memory record representation for directory entries, inode records, delete records, bulk data, and general metadata records.
- `hammer_io`: common header embedded in volumes and buffers for lock state, dirty/running state, buffer-cache association, modify refs, I/O callbacks, and flush/reclaim coordination.
- `hammer_volume`: in-memory wrapper around on-disk volume header and device vnode.
- `hammer_buffer`: in-memory wrapper for on-disk buffers and associated node list.
- `hammer_node`: in-memory wrapper for on-disk B-Tree nodes, including node lock, backing buffer, cursor list, cache list, and CRC/state flags.
- `hammer_node_lock`: recursive node-lock tree used by split/rebalance-style operations.
- `hammer_reserve`: blockmap big-block reservation used by direct write and delayed reuse protection.
- `hammer_undo`: recent undo history entry for avoiding duplicate undo records.
- `hammer_flusher`: master flusher state, sequencing, ready/run lists, transaction, and finalization lock.
- `hammer_mount`: full per-mount runtime state, including RB roots for inodes, volumes, nodes, buffers, undo/reservation trees, blockmaps, flusher, dirty-space counters, volume map, TID state, export state, locks, tokens, and statistics.

Important flags and constants:
- Transaction flags include new-inode and CRC-domain behavior.
- Inode flags cover dirty data, reserved resources, on-disk state, deletion state, read-only snapshot state, flush/reflush state, atime/mtime changes, REDO/RDIRTY state, truncation, and reclaim.
- Record flags distinguish allocated data, RB-tree membership, frontend/backend deletion, committed state, backend interlocks, waiters, delete conversion, and REDO.
- I/O types distinguish volume, metadata buffer, undo buffer, data buffer, and dummy buffer.
- Mount flags track critical errors, flush recovery, and REDO recovery state.
- Checkspace slop constants define reservation conservatism for reblock, mirror, write, create, remove, and emergency paths.

Important inline helpers:
- Lock/reference state checks for `hammer_lock`.
- `hammer_checkspace()` wrapper around `_hammer_checkspace()`.
- Convenience wrappers for lock acquisition, mem-record waits, and no-undo modifications.
- B-Tree node modification helpers, including full-node undo fallback and CRC scheduling through `HAMMER_NODE_NEEDSCRC`.
- `hammer_btree_extract_leaf()` and `hammer_btree_extract_data()` wrappers.
- `hammer_blockmap_lookup()`, which can skip verification when zone verification is disabled and direct-map to zone 2.
- Volume-number bitmap add/delete/test helpers.
- Buffer-to-HAMMER-IO attach/peek helpers.
- Directory localization helper for directory-local inode placement.

Function prototype coverage:
- VFS/vnode entry points and vnode acquisition.
- Inode lookup, creation, syncing, reclaim, unload, and dirtying.
- Volume and buffer installation, lookup, unload, reference/release, and sync/deletion.
- HAMMER object and record operations.
- Cursor navigation, lock upgrade/downgrade, recovery, and cursor mutation notifications.
- B-Tree lookup, iteration, insertion, deletion, propagation, node locking, parent lookup, and diagnostics.
- Block allocation, data allocation, blockmap reserve/finalize/free/dedup/checkspace.
- UNDO/REDO generation and recovery.
- Transaction start/finish and TID allocation.
- Directory entry and bulk-data operations.
- Pseudofs operations and ioctl handlers.
- Low-level I/O operations, direct read/write paths, interlocks, flushing, and error clearing.
- Administrative ioctls: reblock, rebalance, prune, mirror, pseudofs, volume add/delete/list, dedup.
- Flusher and recovery entry points.
- Block-size helpers and fsid conversion.

Architectural role:
- This header is the connective tissue for HAMMER’s kernel implementation. It exposes almost every internal subsystem boundary, so changes here affect the whole filesystem.
- It separates on-disk formats from in-memory synchronization, caching, and transactional behavior.
- The code assumes careful coordination between `fs_token`, `io_token`, HAMMER locks, buffer modify refs, cursor locks, and flusher sequencing.
