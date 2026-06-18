# sources/user-network-fs/nfs-utils/utils/mount/mount_libmount.c

Purpose: libmount-based frontend for NFS mount and umount helpers, replacing local mtab/fstab handling with libmount context management.

Important APIs: `main()` creates a `libmnt_context` and dispatches by program name. `mount_main()` parses helper options via `mnt_context_helper_setopt()`, applies fstab and nfsmount.conf options, prepares the mount, runs `try_mount()`, and finalizes. `umount_main()` prepares unmount, retrieves stored NFS options, optionally sends MNT `UMNT`, performs `umount(2)`, and finalizes. `store_mount_options()` and `retrieve_mount_options()` bridge fs-specific NFS options through mtab or `/dev/.mount/utab`.

Control flow: libmount owns canonicalization, permission checks, option separation, and table updates. Actual NFS work still delegates to `nfsmount_string()`, `nfs4mount()`, or `nfsmount()`. Background mounts daemonize and re-enter `try_mount()`.

State and persistence: globals mirror legacy frontend flags for shared lower layers. Persistent state is maintained by libmount in mtab/utab, with fs attributes used on non-mtab systems.

Dependencies and integration: libmount, mount config glue, NFS protocol mount implementations, string options, error utilities.

Risks: option storage/retrieval must preserve fs-specific NFS options or unmount advisory calls lose server data. Test signals include mount and umount helper modes, restricted user mounts through libmount, utab attribute storage, NFSv4 detection, lazy unmount skip, and background behavior.
