# sources/user-network-fs/libfuse/lib/mount_fsmount.c

## Purpose
Linux new mount API implementation for FUSE using `fsopen`, `fsconfig`, `fsmount`, and `move_mount`. It supports both direct libfuse mounts and setuid-helper sync-init mounts onto a pinned mountpoint fd.

## Important APIs, Types, And Functions
- `ms_flags_to_mount_attrs` converts remaining `MS_*` flags into `MOUNT_ATTR_*`.
- `set_fsconfig_ms_flags` applies superblock-level flags via `fsconfig(FSCONFIG_SET_FLAG)`.
- `apply_fsconfig_opt_fd`, `apply_fsconfig_opt_string`, and `apply_fsconfig_mount_opts` translate legacy comma options into `fsconfig` calls.
- `log_fsconfig_kmsg` reads kernel context diagnostics from the fsopen fd.
- `fuse_kern_fsmount` drives the full new-API mount sequence and records mtab/utab.

## Control Flow
The mount flow builds source/type strings, opens a filesystem context, optionally sets subtype and source, applies flags and options, creates the filesystem, translates mount attributes, creates an unattached mount fd, moves it to either a path or a destination fd, then records the mount. Error paths log fsconfig diagnostics and clean up fsfd/mountfd; after a failed move or mtab update it detaches the temporary mount through `/proc/self/fd/<mountfd>`.

## State And Persistence
No persistent process state. Kernel state is staged in an fsopen context fd until `FSCONFIG_CMD_CREATE`; mount namespace state changes only after `move_mount`. Persistent user-visible state is mount table metadata written through `fuse_mnt_add_mount_helper`.

## Dependencies And Integration Points
Depends on Linux new mount API availability, `mount_flags` from `mount_util.c`, and declarations in `mount_i_linux.h`. It is called by `mount.c`, `fusermount.c` sync-init, and `mount_service.c`.

## Risks
The mapping between legacy `MS_*` flags, fsconfig flags, and mount attributes is subtle; unsupported residual flags produce `ENOTSUP`. Filtering mtab-only and mount-attribute options before fsconfig is essential to avoid kernel rejection. Kernel support varies by version, so fallback paths must remain covered.

## Test Signals
Run with `HAVE_NEW_MOUNT_API` on kernels with and without subtype support, verify `ro/rw` dual handling, unsupported flag fallback, fsconfig error logging, pinned-fd `move_mount`, mtab update failure cleanup, and parity with traditional `mount(2)` options.
