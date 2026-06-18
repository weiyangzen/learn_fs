# File Research: sources/teaching/os161/kern/vfs/vfslist.c

Maintains the global VFS named-device table. Each `knowndev` records a device name, optional raw name, device pointer, device vnode, and mounted or hardwired filesystem. `SWAP_FS` is a sentinel marking a device used as swap.

`vfs_bootstrap` creates the device array, creates the recursive teaching `vfs_biglock`, registers `null:`, and bootstraps `semfs`. The big lock tracks recursion depth and has defensive behavior for unimplemented student locks.

The file implements sync across filesystems, root lookup by device or volume name, device-name lookup for a filesystem, duplicate-name checks, `vfs_adddev`, `vfs_addfs`, mount, unmount, swap attach/detach, and unmount-all. Mountable devices expose both `name` and `nameraw`.

Main risks: coarse recursive locking, linear global table scans, and careful handling of mounted, raw, hardwired, and swap states.
