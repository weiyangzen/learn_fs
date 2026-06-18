# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu.h

Read status: complete, 1091 lines.

Purpose: primary public Data Management Unit interface for consumers. It defines DMU object types, objset operations, buffer holds/users, transaction lifecycle, read/write APIs, object and objset stats, sync writes, traversal, diff, and CRC support.

Key definitions:
- `dmu_object_byteswap_t` enumerates byteswap strategies.
- `DMU_OT()` encodes new object types with byteswap, metadata, and encryption flags.
- `dmu_object_type_t` lists legacy fixed on-disk object types and newer `DMU_OTN_*` encoded variants.
- TXG assignment flags: `TXG_NOWAIT`, `TXG_WAIT`, `TXG_NOTHROTTLE`.
- `dmu_buf_t` is the public buffer shape: object, offset, size, data pointer.
- MOS directory ZAP names are declared as `DMU_POOL_*` constants.
- `dmu_buf_user_t` defines dbuf client eviction callback state.
- `dmu_object_info_t`, `dmu_object_type_info_t`, `dmu_object_byteswap_info_t`, and `dmu_objset_stats_t` define metadata query results.
- `zgd_t` and `dmu_sync_cb_t` support synchronous write completion.

Major API areas:
- Objset lifecycle: hold/own/release/disown/create/clone/snapshot/find/remap.
- Object lifecycle: alloc/claim/reclaim/free/next/set block size/set checksum/set compression/remap.
- Bonus/spill buffer access and mutation.
- Buffer holds, array holds, refcounts, dbuf users, user eviction waiting, block pointer access, dirty marking, and raw crypto parameter setting.
- Transaction creation, holds, assignment, wait, commit, abort, callback registration, and netfree marking.
- Data operations: range free, read/write, uio read/write, page write, prealloc, ARC buffer request/assign/return, raw conversion, xuio helpers, prefetch.
- Object/objset info and space/stat queries.
- Dataset/listing helpers, objset user pointer registration, txg lookup.
- `dmu_sync()`, offset hole/data search, object wait-synced, init/fini, objset traversal, `dmu_diff()`.

Important implementation constraints:
- Public comments define transaction ordering: create transaction, hold possible modified objects, assign to TXG, then modify buffers.
- Dbuf users must not reference the dbuf from eviction callbacks because callbacks run after eviction processing has begun and without dbuf mutex guarantees.
- `DMU_MAX_ACCESS` caps one operation including metadata at 32 MiB.
- New on-disk object types should use encoded `DMU_OTN_*` instead of extending fixed enum values.

Dependencies: ZFS context, credentials, ZFS property types, compression/priority enums, SPA/ZIO/dsl/dnode forward declarations.

Research notes:
- This is the highest-level interface in the group and is consumed by ZPL, ZVOL, ZAP, DSL, SPA, send/receive, and tools.
- Many declarations are implemented across multiple `.c` files, not a single DMU implementation file.
