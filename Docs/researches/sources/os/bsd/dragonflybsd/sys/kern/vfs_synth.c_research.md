# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_synth.c

## Role

This small file creates and exposes a synthetic devfs-backed lookup root used to obtain device vnodes by name from kernel code. It mounts a private devfs instance during VFS initialization and provides `getsynthvnode()` as the lookup interface.

## Main Responsibilities

- Maintains global synthetic devfs state:
  - `synth_mp`
  - `synth_vp`
  - `synth_inited`
  - `synth_synced`
- Initializes a dummy devfs mount in `synthinit()`:
  - Allocates a root mount with `vfs_rootmountalloc("devfs", "dummy", &synth_mp)`.
  - Mounts it through `VFS_MOUNT()`.
  - Obtains its root vnode through `VFS_ROOT()`.
  - Allocates the mount root namecache handle with `cache_allocroot()`.
  - Drops the temporary root vnode lock/reference and marks the synthetic layer initialized.
- Resolves device names with `getsynthvnode()`:
  - Asserts the synthetic mount is initialized.
  - Calls `sync_devs()` on the first two lookups to ensure devfs/disks are populated.
  - Performs `nlookup_init_root()` relative to the synthetic devfs root.
  - Returns a VX-locked/refd vnode via `vget(vp, LK_EXCLUSIVE)`.

## Synchronization and Lifetime Model

- Initialization is performed via `SYSINIT(synthinit, SI_SUB_VFS, SI_ORDER_ANY, ...)`, so callers expect the synthetic mount to exist after VFS startup.
- `getsynthvnode()` transfers the namecache result out of `nlookupdata`, then unlocks the namecache handle after `vget()`.
- The returned vnode is locked and referenced; callers must release it with the normal vnode path.

## Cross-File Relationships

- Uses the general mount operation wrappers/macros implemented around `VFS_MOUNT()` and `VFS_ROOT()`.
- Relies on DragonFly namecache/nlookup primitives that are heavily used by `vfs_syscalls.c`.
- Produces regular vnodes that flow into the same vnode lifecycle machinery described in `vfs_subr.c`.

## Research Notes

- This is a specialized kernel convenience layer, not a general synthetic filesystem implementation.
- Error handling is intentionally strict during init: failure to allocate, mount, or root the devfs instance panics.
- Runtime lookup failures are nonfatal and return `NULL`, with warnings for errors other than `ENOENT`.
