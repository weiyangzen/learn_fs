# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null.h

This header defines the core data structures, flags, macros, and prototypes for FreeBSD nullfs, a stackable loopback filesystem layer.

Key definitions:
- `struct null_mount` stores the lower mount, referenced lower root vnode, mount flags, and upper/notification registration nodes.
- `struct null_node` stores the per-upper-vnode mapping to a referenced lower vnode, a back pointer to the upper vnode, and vnode flags.
- Mount flags:
  - `NULLM_CACHE`: cache free nullfs vnodes.
  - `NULLM_NOUNPBYPASS`: disable UNIX-domain socket bypass behavior.
- Vnode flags:
  - `NULLV_NOUNLOCK`: reclaim path should not unlock the lower vnode.
  - `NULLV_DROP`: vnode should be recycled/dropped, typically after unlink/removal.
- Conversion helpers: `MOUNTTONULLMOUNT`, `VTONULL`, `VTONULL_SMR`, `NULLTOV`, and `NULLVPTOLOWERVP`.

Exported interfaces:
- Lifecycle: `nullfs_init()`, `nullfs_uninit()`.
- Node cache: `null_nodeget()`, `null_hashget()`, `null_hashrem()`.
- VOP bypass: `null_bypass()`.
- VOP vectors: `null_vnodeops`, `null_vnodeops_no_unp_bypass`.
- `null_is_nullfs_vnode()` tests whether a vnode uses one of the nullfs operation vectors.
- `null_node_zone` is the UMA allocation zone for `struct null_node`.

Research-relevant notes:
- The header exposes SMR-aware access to `v_data`, which is central to lock/reclaim race handling in `null_vnops.c`.
- `NULLVPTOLOWERVP` expands to a diagnostic checker when `DIAGNOSTIC` is enabled.
