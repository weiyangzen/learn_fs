# File Research: sources/teaching/minix/minix/servers/vfs/vnode.c

## Purpose
Manages VFS vnode table entries, including allocation, lookup, locking, duplication, reference release, and reference cleanup at underlying file servers.

## Main Entry Points
- `init_vnodes()` initializes the vnode table and locks.
- `get_free_vnode()` finds an unused, unlocked vnode slot.
- `find_vnode()` finds an active vnode by FS endpoint and inode number.
- `is_vnode_locked()` checks active or pending lock state.
- `lock_vnode()`, `unlock_vnode()`, `upgrade_vnode_lock()` wrap TLL.
- `dup_vnode()` increments VFS reference count.
- `put_vnode()` drops a vnode reference and sends `req_putnode` when the last VFS reference is gone.
- `vnode_clean_refs()` reduces accumulated FS-side references to one.

## Reference Model
`v_ref_count` tracks VFS users. `v_fs_count` tracks references held at the underlying file server. `put_vnode()` avoids sending a file-server put on every VFS ref decrement; it only sends when VFS refcount reaches zero, or trims excessive FS refs when `v_fs_count > 256`.

Mapped inode references are separately tracked with `v_mapfs_e`, `v_mapinode_nr`, and `v_mapfs_count`, and released from mapped FS when needed.

## Locking
Vnodes use TLL lock modes mapped in `vnode.h`. `put_vnode()` obtains `VNODE_OPCL`, upgrades to exclusive access when releasing the final reference, and asserts that a final put cannot happen while the current worker already owns the lock.

## Debugging
Lock-debug builds provide checks for locks still held by a process and verify the current worker is not left in vnode lock queues.

## Risks and Notes
`get_free_vnode()` only considers slots with zero refs and no lock/pending lock. `put_vnode()` panics on invalid reference counters and logs stack traces if `req_putnode` fails.
