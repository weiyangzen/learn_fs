# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_init.c

## Purpose
Bootstraps the NetBSD VFS layer: sysctl setup, vnode table/namecache initialization, vnode operation vector construction, generic dirhash/hooks initialization, mount authorization listener setup, VFS module initialization, and filesystem attach/detach/reinit support.

## Main Interfaces
- `vn_default_error`: generic default vnode operation returning `EOPNOTSUPP`.
- `sysctl_vfs_setup`: creates generic VFS sysctls.
- `vfs_opv_init`, `vfs_opv_free`: allocate/fill/free vnode operation vectors.
- `vfs_opv_init_explicit`, `vfs_opv_init_default`: install explicit vnode ops and default missing slots.
- Debug `vfs_op_check`: validates vnode operation descriptor offsets/count.
- `usermount_common_policy`: shared policy for unprivileged mounts.
- `mount_listener_cb`: kauth listener for mount permissions and device access.
- `vfsinit`: top-level VFS initialization path.
- `vfs_delref`, `vfs_attach`, `vfs_detach`, `vfs_reinit`: manage filesystem type registration and lifecycle.

## State And Control Flow
`vfsinit` creates generic sysctls, initializes vnode and namecache subsystems, validates operation descriptors in debug builds, initializes special dead/fifo/spec vnode operations, starts dirhash and VFS hook support, registers a kauth mount listener, initializes statically included VFS modules, and sets up filesystem kqueue filtering. `vfs_attach` checks for duplicate filesystem names or `makefstype` collisions, initializes vnode ops, calls the filesystem init routine, and links the `vfsops` into `vfs_list`. `vfs_detach` refuses busy filesystems, removes the entry, calls cleanup, and frees vnode op vectors.

## Dependencies And Integration
Uses vnode operation descriptors, special vnode operation tables, sysctl, kauth, module initialization, vfs list locking, dirhash, namecache, VFS hooks, deadfs/fifofs/specfs, and filesystem-provided `vfsops`.

## Risks And Edge Cases
- Vnode operation descriptor mistakes panic during initialization if an operation offset is missing or inconsistent.
- Filesystem type collisions are checked both by name and by `makefstype` numeric value.
- `vfs_detach` depends on accurate `vfs_refcount`; busy filesystems cannot be detached.
- Unprivileged mount policy requires `nodev` and `nosuid`, preserves existing `noexec`, and rejects exported mounts.
- Reinit temporarily increments each filesystem refcount while calling its callback outside the global list lock.

## Filesystem Relevance
Very high. This is core VFS registration and initialization infrastructure for all NetBSD filesystem modules.
