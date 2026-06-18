# File Research: sources/virtualization/libguestfs/lib/fuse.c

Purpose: Implements `mount-local`, `mount-local-run`, and `umount-local`, exposing the mounted guest filesystem through libfuse when libguestfs is built with FUSE support.

Key behavior:
- Defines FUSE operations for lookup, access, readlink, directory read, node creation/removal, rename/link, chmod/chown, truncate, utimens, open, read, write, statfs, fsync, xattrs, release, and flush.
- Read and write operations cap single protocol transfers at 2 MiB.
- Read-only mount mode rejects write-capable operations with `EROFS`.
- `readdir` prepopulates three short-lived directory caches: lstat results, xattrs, and readlink targets.
- Cache entries are keyed by full path in gnulib hash tables and expire after `ml_dir_cache_timeout`.
- `guestfs_impl_mount_local` builds FUSE args, mounts the local mountpoint, creates the FUSE handle, stores `g->localmountpoint`, and initializes caches.
- `guestfs_impl_mount_local_run` verifies `/` is mounted, enters `fuse_loop`, then destroys FUSE state and clears the mountpoint.
- `guestfs_impl_umount_local` shells out to `guestunmount` with optional retry.
- If `HAVE_FUSE` is false, all public entry points return `ENOTSUP`.

Dependencies and state:
- Uses libfuse 2.6 APIs, generated guestfs filesystem actions, `guestfs_last_errno`, `guestfs_int_new_command`, `guestunmount`, and gnulib hash helpers.
- Mutates FUSE-specific fields in `guestfs_h`: `localmountpoint`, `fuse`, `ml_dir_cache_timeout`, `ml_read_only`, `ml_debug_calls`, and cache hash tables.
- A global `mount_local_lock` protects `g->localmountpoint`.

Risks:
- FUSE callbacks rely on the same `guestfs_h`; concurrency safety depends on public action locking and FUSE threading behavior.
- `readdir` ignores offsets, matching common examples but potentially weak for very large directories.
- xattr flag semantics are not fully supported because the underlying guestfs API ignores setxattr flags.
