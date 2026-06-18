# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dnode.h

Read status: complete, 603 lines.

Purpose: defines physical and in-core dnode layout, dnode constants, large-dnode support, dnode handles, allocation/free/sync APIs, cacheability macros, and dnode kstats.

Key definitions:
- Hold flags: `DNODE_MUST_BE_ALLOCATED`, `DNODE_MUST_BE_FREE`, `DNODE_DRY_RUN`.
- Offset search flags: `DNODE_FIND_HOLE`, `DNODE_FIND_BACKWARDS`, `DNODE_FIND_HAVELOCK`.
- Fixed constants define dnode sizes, indirect block shift limits, object/offset limits, dnodes per block/level, maximum levels, bonus sizes, slot sentinels, and spill pointer location.
- Dnode flags track used-byte encoding, user/group/project accounting, and spill block pointer presence.
- Large dnode comments explain variable-size dnodes from 512 bytes to 16 KiB and the relationship between on-disk `dn_extra_slots` and in-memory `dn_num_slots`.

Key structures and APIs:
- `dnode_phys_t` is the on-disk dnode: type, block shifts, levels, block pointer count, bonus type, checksum/compression, flags, data block size, bonus length, extra slots, max block id, used space, padding protected by MACs, block pointers/bonus/spill union.
- `dnode_t` is the in-core dnode: structure lock, objset/object/dbuf/handle/phys pointers, cached physical fields, next-TXG pending field arrays, dirty links, dirty records, free ranges, TXG/refcount state, dbuf AVL tree, bonus dbuf, spill state, sync write parent zio, old/new id accounting state, and embedded zfetch state.
- `dnode_handle_t` uses `zrlock_t` to protect dnode moves.
- `dnode_children_t` attaches child dnode handles to a meta-dnode dbuf user.
- `free_range_t` records block ranges pending free.
- APIs cover special dnode open/close, bonus/spill mutation, hold/ref/release, try-claim, dirty/sync, allocate/reallocate/free, byteswap/verify, level/block-size changes, free ranges, space accounting, new block ids, block-free lookup, init/fini, hole/data search, dbuf/bonus eviction, interior slot freeing, and remap checks.

Important implementation constraints:
- `dn_struct_rwlock` protects tree structure and pending structural changes.
- `dn_dbufs` can contain duplicate logical dbufs when evicting, so lookup uses walks/search sentinel semantics instead of direct AVL uniqueness by logical key.
- Handles prevent dnode movement from invalidating dbuf-owned dnode access.
- Dnode MAC coverage matters for encrypted datasets; new fields in protected padding require crypto path review.

Dependencies: ZFS context, AVL, SPA, TXG, ZIO, refcount, zfetch, zrlock, multilist.

Research notes:
- This is the core object metadata header for DMU object storage.
- `dnode_stats_t` provides detailed counters for dnode hold allocation/free paths, allocation races, buffer eviction, and dnode movement.
