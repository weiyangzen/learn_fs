# File Research: sources/os/linux/linux/fs/nfs/super.c

Implements NFS filesystem registration, superblock operations, mount display/statistics, mount negotiation, superblock sharing, remount validation, and NFSv4 module parameters.

Key behavior:
- Defines and exports `nfs_sops` with inode allocation/free, writeback, statfs, eviction, unmount cancellation, and show callbacks.
- `register_nfs_fs()` registers NFS and optional NFSv4 filesystems, registers sysctls, installs the NFS access-cache shrinker, and registers NFSv4.2 server-side-copy client hooks.
- `nfs_statfs()` calls protocol-specific statfs, translates byte counts to VFS block counts, and zaps parent caches on stale file handles.
- Mount option rendering covers protocol version, I/O sizes, attribute-cache timers, hard/soft mode, lookup cache mode, transport, ports, timeout/retransmit, security flavor, TLS transport security, mountd options, FS-Cache, migration, local locking, aligned writes, and eager/write-wait policy.
- `nfs_show_stats()` emits mount options, mount age, capability bits, NFSv4 attributes/session/pNFS/lease data, security flavor, per-CPU I/O counters, and RPC client stats.
- `nfs_umount_begin()` kills pending ACL and main RPC client tasks during unmount.
- Mountd negotiation requests the root file handle, verifies or selects an auth flavor, avoids selecting `AUTH_NULL` unless needed, and creates the server using the selected flavor.
- Remount rejects changes to options that are incompatible with an existing superblock, while preserving `noac` implying synchronous writes.
- `nfs_fill_super()` sets VFS operations, xattrs, block size, timestamp granularity/range, export ops, magic, maxbytes, sysfs name, and security-mount-option tracking.
- Superblock comparison checks server address, namespace, fsid, user namespace, security mount options, and shareable mount options.
- FS-Cache cookie setup handles ordinary mounts and cloned mounts.
- `nfs_get_tree_common()` handles superblock lookup/sharing, BDI setup, root dentry acquisition, and activation.
- `nfs_kill_super()` moves sysfs identity back to the server name, kills the anonymous superblock, releases FS-Cache state, and frees the server.
- NFSv4 module parameters include callback port/thread count, idmap cache timeout, idmapping disable flag, session slot limits, implementation ID sending, unique client ID, lost-lock recovery, and delay retransmit behavior.

Important interactions:
- Central bridge between fs_context mount parsing/server creation and VFS superblock lifecycle.
- Uses `sysfs.c` for server kobject naming and `sysctl.c` for tunables.
- Shares server/client objects across mounts unless `nosharecache`/unshared semantics or option mismatches prevent sharing.
