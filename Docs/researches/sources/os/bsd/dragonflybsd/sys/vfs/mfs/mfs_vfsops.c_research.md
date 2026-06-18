# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfs_vfsops.c

## Scope

Implements the memory filesystem as a kernel block device backed by user address space and mounted through UFS/FFS operations.

## APIs And Behavior

- Registers `mfs_vfsops`, delegating most filesystem semantics to UFS/FFS (`ffs_unmount`, `ufs_root`, `ffs_sync`, `ffs_vget`, exports, filehandles).
- Defines `mfs_ops` device methods for open, close, read/write via physio, and strategy.
- `mfsopen()` validates the device has an attached `mfsnode`.
- `mfsclose()` marks the filesystem inactive and wakes the service thread.
- `mfsstrategy()` bounds-checks bio offsets, clips EOF reads, queues I/O to the service thread, or services directly if called by that thread.
- `mfs_mount()` handles updates/export changes, creates a synthetic `/dev/mfs<pid>` device, initializes `mfsnode`, resolves the devfs vnode, sets pager size, and mounts FFS on the device.
- `mfs_start()` holds the backing process, services queued bios, handles signals by attempting unmount, destroys the device, and frees `mfsnode` on exit.
- `mfs_doio()` implements read, write, and `BUF_CMD_FREEBLKS` using `copyin`, `copyout`, and `MADV_FREE`.

## Dependencies

Depends on DragonFly device, vnode, mount, bio queue, VM, devfs, signal, UFS/FFS, and buffer infrastructure.

## Risks And Invariants

The backing process must remain resident while servicing I/O. Bounds checking in `mfsstrategy()` prevents access outside the supplied memory image. `FREEBLKS` only frees page-aligned portions. Root MFS mount is explicitly not configured and panics if attempted.
