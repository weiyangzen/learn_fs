# File Research: sources/teaching/minix/minix/servers/vfs/vmnt.c

## Purpose
Manages the virtual mount table: initialization, allocation, lookup, lock wrappers, endpoint unmapping, and mount path refresh.

## Main Entry Points
- `init_vmnts()` clears all mount entries and initializes their TLL locks.
- `get_free_vmnt()` finds and resets a free mount table slot.
- `find_vmnt()` locates an in-use mount by FS endpoint.
- `mark_vmnt_free()` marks an entry unused.
- `lock_vmnt()`, `unlock_vmnt()`, `upgrade_vmnt_lock()`, `downgrade_vmnt_lock()` wrap TLL operations.
- `vmnt_unmap_by_endpt()` handles a file-server endpoint disappearing.
- `fetch_vmnt_paths()` refreshes canonical mount paths.

## State Management
`clear_vmnt()` resets endpoint/device, flags, mounted/root vnode pointers, label, and communication counters. A mount is considered free when `m_dev == NO_DEV`.

## Locking
`lock_vmnt()` maps `VMNT_EXCL` to an initial write lock and then upgrades. It rejects attempts by a file server to lock its own mount with `EDEADLK`. Lock-debug builds track read locks in `fp->fp_vmnt_rdlocks`.

## Endpoint Failure Handling
`vmnt_unmap_by_endpt()` marks a mount free, cancels FS communication, invalidates filps by endpoint, and releases the mount point vnode when the mount was successfully attached.

## Path Refresh
`fetch_vmnt_paths()` canonicalizes mount paths, skipping unused mounts and PFS. If canonicalization fails, it temporarily uses the mounted-on vnode as working directory and retries with the mount point basename.

## Risks and Notes
`fetch_vmnt_paths()` temporarily mutates `fp->fp_wd`; callers must assume process context is meaningful. `check_vmnt_locks()` panics if any vmnt remains locked or pending.
