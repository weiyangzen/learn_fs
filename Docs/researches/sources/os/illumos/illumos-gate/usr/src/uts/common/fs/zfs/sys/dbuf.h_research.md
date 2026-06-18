# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dbuf.h

Read status: complete, 450 lines.

Purpose: private DMU buffer implementation interface. Defines dbuf state, dirty records, in-core dbuf layout, hash table layout, cache policy macros, and internal dbuf lifecycle/read/write APIs.

Key structures and APIs:
- Read flags include `DB_RF_MUST_SUCCEED`, `DB_RF_CANFAIL`, `DB_RF_NOPREFETCH`, `DB_RF_NEVERWAIT`, `DB_RF_CACHED`, and `DB_RF_NO_DECRYPT`.
- `dbuf_states_t` models the dbuf state machine: search sentinel, uncached, fill, nofill, read, cached, evicting.
- `dbuf_dirty_record_t` records per-TXG dirty state and distinguishes indirect dirty children from leaf data/override/raw-encryption parameters.
- `dmu_buf_impl_t` wraps public `dmu_buf_t` with objset/dnode/parent/hash metadata, block identity, state locks, ARC buffer pointer, holds, dirty records, AVL/list cache linkage, user callback data, and eviction flags.
- `dbuf_hash_table_t` exposes the global dbuf hash table shape for mdb.
- Core APIs cover hold/find/read/prefetch/refcount/release, dirtying, ARC buffer assignment/loaning, embedded writes, dirty-list syncing, block-pointer release, parent locking, remap checks, free ranges, and cache initialization.

Important implementation constraints:
- `db_rwlock` protects indirect/meta-dnode tree structure; documented ordering is dnode structure lock before dbuf lock.
- `db_mtx` protects mutable buffer state, holds, data pending, dirty records, cache status, and user fields.
- Dbuf cacheability is derived from objset primary/secondary cache policy and metadata classification.
- Dnode access uses `dnode_handle_t` plus `zrlock` macros to survive dnode movement.

Dependencies: DMU, SPA, TXG, ZIO, ARC, refcounts, zrlock, multilist.

Research notes:
- This header is the main boundary between public DMU buffers, ARC storage, and dnode block-tree structure.
- Debug macros integrate dbuf and block pointer information into dataset-level debug logging.
