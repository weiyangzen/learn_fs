# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_tnode.c

Tmpfs tmpnode lifecycle and file storage accounting: swap reservation, anon-map growth, tmpnode initialization, and truncation.

Key responsibilities:
- Reserves backing swap/memory for tmpfs file growth in `tmp_resv()`, enforcing per-mount `tm_anonmax`, system free-space policy, and zone reservations.
- Releases reservations in `tmp_unresv()` during truncation.
- Grows a regular file's anonymous-slot array in `tmpnode_growmap()`, initially allocating at least `TMP_INIT_SZ` slots.
- Initializes tmpnodes and backing vnodes in `tmpnode_init()`, setting mode, type, uid/gid, fsid, nodeid, generation, timestamps, vnode ops, mount linkage, and global mount tmpnode list membership.
- Truncates tmpnodes in `tmpnode_trunc()`, handling growth, shrink, partial-page zeroing, anon-page freeing, anon array release at size zero, symlink constraints, and directory truncation.

Dependencies:
- Uses anon subsystem calls: `anon_checkspace`, `anon_try_resv_zone`, `anon_unresv_zone`, `anon_create`, `anon_grow`, `anon_pages`, `anon_free`, and `anon_release`.
- Uses VM/vnode helpers such as `pvn_vpzero`, `vn_has_cached_data`, `vn_alloc`, `vn_setops`, and `vn_exists`.
- Uses tmpfs directory helper `tdirtrunc()` and vnode ops `tmp_vnodeops`.

Concurrency and locking:
- `tmp_resv()`, `tmp_unresv()`, `tmpnode_growmap()`, and `tmpnode_trunc()` assert the appropriate tmpnode rwlocks, especially `tn_rwlock` and `tn_contents`.
- Mount-wide tmpnode list and `tm_anonmem` accounting are protected by `tm_contents`.
- `tmpnode_trunc()` temporarily drops `tn_contents` while zeroing a partial final page to avoid VM re-entry deadlocks.

Notable risks:
- Reservation size is page-rounded and intended to track file size, including holes grown by truncate.
- Shrink updates `tn_size` before zeroing partial pages so concurrent faults do not instantiate pages beyond the new EOF.
- `tmpnode_init()` uses a pointer-derived 32-bit node id; generation numbers are used to disambiguate reuse in fids.
