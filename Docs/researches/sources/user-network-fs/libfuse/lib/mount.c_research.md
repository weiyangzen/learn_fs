# sources/user-network-fs/libfuse/lib/mount.c

## Purpose
Linux-specific libfuse mount implementation. It parses libfuse mount options, opens `/dev/fuse`, attempts an in-process kernel mount, falls back to `fusermount3` when required, and exposes unmount/version helpers used by the public libfuse mount path.

## Important APIs, Types, And Functions
- Uses `struct mount_opts` from `mount_i_linux.h` to track parsed option state: `flags`, `auto_unmount`, `blkdev`, `fsname`, `subtype`, `kernel_opts`, `mtab_opts`, and `fusermount_opts`.
- `parse_mount_opts` and `destroy_mount_opts` own option allocation and cleanup.
- `fuse_kern_mount_prepare` validates the mountpoint, opens the configured FUSE character device, and appends `fd=`, `rootmode=`, `user_id=`, and `group_id=` to kernel options.
- `fuse_kern_do_mount` performs traditional `mount(2)` using source/type strings from `mount_util.c`, records the mount table entry, and signals `FUSE_MOUNT_FALLBACK_NEEDED` on `EPERM`.
- `fuse_kern_mount` builds mtab options, tries the direct mount path, handles `auto_unmount`, and falls back to `fuse_mount_fusermount`.
- `mount_fusermount_obtain_fd` and `fuse_fusermount_proceed_mnt` implement the new sync-init exchange with `fusermount3`.
- `fuse_kern_unmount` closes the device fd, checks `POLLERR`, and unmounts directly or through `fusermount3`.

## Control Flow
Option parsing routes recognized options into kernel, mtab-only, subtype, or helper-only buffers. Direct mounting first opens `/dev/fuse`, appends required fd/root/user options, builds `fuse`/`fuseblk` type and source, and calls `mount(2)`. If subtype mounting returns `ENODEV`, it retries legacy source/type forms. On `EPERM`, libfuse assumes an unprivileged mount needs the setuid helper. The fallback creates a socketpair, exposes one end through `_FUSE_COMMFD`, spawns `fusermount3`, receives the opened FUSE fd via `SCM_RIGHTS`, and optionally keeps the socket open for auto-unmount.

## State And Persistence
The file stores no persistent global state beyond environment variables used for helper IPC. It mutates `struct mount_opts` allocations and writes mount table state indirectly through `fuse_mnt_add_mount_helper`. Auto-unmount intentionally leaks a socket fd so `fusermount3` can detect process death.

## Dependencies And Integration Points
Depends on libfuse option parsing, `mount_util.c` for device/type/source/mtab helpers, `mount_fsmount.c` when `HAVE_NEW_MOUNT_API` is enabled, and `fusermount3` installed under `FUSERMOUNT_DIR` or in `PATH`. The public libfuse mount code calls this file through declarations in `mount_common_i.h` and `mount_i_linux.h`.

## Risks
Security risk is concentrated around helper IPC, environment variables, and mountpoint path stability. The code pins file descriptors for sync-init via the helper path but the direct in-process `mount(2)` path resolves by path. The `posix_spawn` helper result is not fully checked when no pid is requested. Auto-unmount deliberately leaves an fd without `FD_CLOEXEC`, which is intentional but easy to misinterpret as a leak.

## Test Signals
Exercise root direct mount, unprivileged helper fallback, subtype `ENODEV` retry, `auto_unmount`, sync-init status exchange, invalid `_FUSE_COMMFD`, missing `/dev/fuse`, `FUSE_KERN_DEVICE` override, mtab option composition, and unmount behavior when the kernel fd already reports `POLLERR`.
