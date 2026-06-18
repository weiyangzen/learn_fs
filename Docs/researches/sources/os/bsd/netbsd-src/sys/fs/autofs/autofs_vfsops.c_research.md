# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vfsops.c

## Summary
Implements AUTOFS VFS operations and module lifecycle.

## Main Responsibilities
- Allocate/destroy global AUTOFS softc, pools, condition variable, mutex, and timeout workqueue.
- Mount autofs instances by copying user options/prefix, creating root node, and setting statvfs metadata.
- Support `MNT_UPDATE` as cache flush.
- Support `MNT_GETARGS` by copying mount metadata back to userland.
- Unmount by flushing vnodes, failing outstanding requests for the mount, deleting all nodes, and freeing mount state.
- Load vnodes from autofs node pointers through vcache.
- Report empty synthetic statvfs values.
- Register sysctl tunables: debug, mount-on-stat, timeout, cache, retry attempts, retry delay, interruptible.
- Attach/detach VFS and, for loadable modules, character device switch.

## Key Interfaces
- `autofs_mount()`, `autofs_unmount()`, `autofs_root()`, `autofs_loadvnode()`, `autofs_init()`, `autofs_done()`.

## Risks
Unmount waits for outstanding daemon requests to drain by marking them done with `ENXIO`. Node deletion assumes vnodes are flushed and no new triggers can appear. Module unload is blocked while `/dev/autofs` is open.
