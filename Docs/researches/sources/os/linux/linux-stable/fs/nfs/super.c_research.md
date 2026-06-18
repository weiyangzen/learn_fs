# File Research: sources/os/linux/linux-stable/fs/nfs/super.c

Purpose: Handles NFS client filesystem registration, superblock lifecycle, statfs, mount option display, mount authentication negotiation, remount checks, and module parameters.

Key responsibilities:
- Defines `nfs_sops` superblock operations.
- Registers/unregisters NFS and optional NFSv4 filesystems, NFS sysctl, ACL shrinker, and SSC ops.
- Implements active superblock references via `nfs_sb_active` / `nfs_sb_deactive`.
- Implements `nfs_statfs`, translating NFS byte counts into VFS block counts.
- Renders mount options and stats for `/proc/mounts` and mountstats:
  - protocol version, sizes, attribute cache timers, locking, transport, security flavor, xprtsec, fscache, pNFS, sessions, NFSv4 lease data, and counters.
- Handles mountd negotiation for v2/v3, including security flavor selection and fallback.
- Implements `nfs_try_get_tree`, `nfs_get_tree_common`, superblock sharing comparison, and `nfs_kill_super`.
- Validates remount compatibility and probes the server on remount.
- Defines NFSv4 module parameters such as callback port/thread count, idmap behavior, session slots, implementation ID, lost-lock recovery, and delay retransmission.

Integration:
- Ties fs_context mount data to `nfs_server` creation through version-specific rpc ops.
- Coordinates with sysfs server naming, fscache cookies, export ops, security mount option compatibility, SUNRPC stats, pNFS, and NFSv4 callback/idmap code.
- Used by all NFS protocol versions.

Risks and notes:
- Superblock reuse is conservative and compares address, fsid, user namespace, selected auth flavor, mount flags, sizes, cache timers, and security options.
- `noac` implies synchronous superblock behavior.
- Binary legacy mount data can skip normal remount option checks.
