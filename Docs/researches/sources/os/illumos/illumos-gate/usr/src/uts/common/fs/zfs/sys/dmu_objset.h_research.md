# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_objset.h

Read status: complete, 268 lines.

Purpose: private objset physical and in-core definitions plus objset implementation APIs.

Key structures and APIs:
- `objset_phys_t` stores the meta dnode, ZIL header, type/flags, encryption MACs, and optional user/group/project accounting dnodes across V1/V2/V3 physical sizes.
- `objset_t` stores dataset/spa links, physical buffer, encryption state, special dnode handles, ZIL pointer, tunable property cache, root block pointer, sync state, dirty dnode lists, object allocation hints, user-used locking, user pointer, SA state, and upgrade task state.
- Macros detect physical feature availability by objset buffer size and expose special dnodes.
- Public/internal APIs cover hold/own/release/disown, ownership refresh, stats/space, find/prefetch, dbuf eviction, sync, create/open/evict, user quota updates/upgrades, encryption compatibility checks, name parsing, dirty space accounting, and init/fini.

Important implementation constraints:
- Special dnodes have no parent and are exempt from dnode movement but still use handles for uniform dbuf access.
- `os_rootbp` points to a block pointer protected by the dataset’s `ds_bp_rwlock`.
- Object allocation uses both `os_obj_lock` and per-CPU next-object hints.
- User/group/project accounting objects are guarded by `os_userused_lock`.

Dependencies: SPA, ARC, TXG, dnode, ZIO, ZIL, SA, ZFS ioctl/property types.

Research notes:
- This header bridges objset physical layout, DMU object allocation, ZIL, quota accounting, and dataset encryption state.
