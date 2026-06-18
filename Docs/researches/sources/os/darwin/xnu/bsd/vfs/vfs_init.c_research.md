# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_init.c

## Scope

This file initializes core VFS infrastructure: vnode operation vectors, vnode tables, filesystem event and name-cache subsystems, static filesystem registrations, dead mount state, VFS locks, dynamic filesystem table insertion/removal, and special-device hash locking.

## Public And Internal APIs Covered

- Operation setup: `vn_default_error()`, `vfs_op_init()`, `vfs_opv_init()`.
- VFS initialization: `vfsinit()`.
- Lock helpers: `vnode_list_lock()`, `vnode_list_unlock()`, `mount_list_lock()`, `mount_list_unlock()`, `mount_lock_init()`, `mount_lock_destroy()`.
- Filesystem registration: `vfstable_add()` and `vfstable_del()`.
- Special hash lock helpers: `SPECHASH_LOCK_ADDR()`, `SPECHASH_LOCK()`, `SPECHASH_UNLOCK()`.

## Control Flow And Behavior

`vfs_op_init()` clears vnode operation vector pointers, assigns operation offsets, and skips disabled operations. `vfs_opv_init()` allocates each operation vector, installs filesystem/layer implementations, validates operation descriptors, and fills missing entries with the vector default operation.

`vfsinit()` initializes vnode tables, VFS events, name cache, operation vectors, all statically configured filesystems, authorization scope, and the dead mount. It also initializes compression support, namespace resolver support, and exclave filesystem support when configured.

`vfstable_add()` registers a filesystem in the first empty static slot or dynamically allocates a `vfstable` when slots are exhausted, links it into `vfsconf`, and registers a sysctl node when needed. `vfstable_del()` unlinks a registered filesystem, unregisters sysctl state, clears static slots, or frees dynamic entries.

## State And Data Structures

- Defines `mount_zone`, VFS SMR domain `vfs_smr`, and static `dead_mount_store`.
- Maintains vnode list, mount, mount list, special hash, and package-extension locks.
- Initializes `dead_mountp` with conservative local/dead mount flags and default I/O constraints.
- Updates global filesystem counters: `numused_vfsslots`, `numregistered_fses`, and `maxvfstypenum`.

## Dependencies

Depends on global vnode operation descriptor arrays, VFS configuration table `vfsconf`, sysctl registration, name cache, vnode authorization, MAC labels, quota/compression/exclave feature gates, lock primitives, and mount/vnode internals.

## Risks And Invariants

- Every operation vector must define `vnop_default`; missing defaults panic.
- Operation descriptors must be present in the global descriptor list unless disabled.
- `vfstable_del()` expects the mount-list mutex to be held by its caller.
- Dynamic `vfstable` deletion temporarily drops and reacquires the mount-list lock around freeing memory.
- `dead_mountp` is a constant pointer to static storage and is initialized late in `vfsinit()`.
