# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode_impl.h

Read completely: 162 lines.

Private vnode implementation header for kernel/kmemuser builds. It wraps the public `struct vnode` in `struct vnode_impl` with cache, LRU, syncer, namecache, state, and lock metadata used by the vnode subsystem.

Core structures:
- `enum vnode_state` models vnode-cache lifecycle: active, marker, loading, loaded, blocked, reclaiming, and reclaimed.
- `struct vcache_key` keys vnodes by mount plus filesystem-provided key bytes.
- `struct vnode_impl` embeds `struct vnode`, vnode-cache key, private `vnode_klist`, LRU/syncer/hash/mount-list linkages, state, namecache tree/list and cached credentials/mode, vnode lock, and namecache locks.
- Conversion macros map between public vnode pointers and implementation objects.

APIs:
- Diagnostic state assertions via `_vstate_assert`, `VSTATE_ASSERT`, and `VSTATE_ASSERT_UNLOCKED`.
- Internal helpers for state names, marker allocation/free/testing, anonymizing cache keys, acquiring cached vnodes, try-acquire, and draining vnodes.
- Declares the `vfs` SDT provider.

Risks and notes:
- Lock annotations document separate vnode-cache, drain, interlock, namecache, mount-list, and syncer locks; ordering matters for deadlock avoidance.
- Marker vnodes are stable special cases and must not be treated like normal filesystem-backed vnodes.
