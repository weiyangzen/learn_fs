# sources/user-network-fs/samba/source3/smbd/quotas.c

## Purpose
This file provides smbd's `disk_quotas` implementation: a best-effort way to report share free/total space according to user or group quota limits instead of raw filesystem capacity. It contains legacy Solaris/NFS quota code for builds without the newer sysquotas interface and a VFS-backed implementation when `HAVE_SYS_QUOTAS` is available.

## Important APIs, Types, And Functions
The exported API is `disk_quotas(connection_struct *conn, struct files_struct *fsp, uint64_t *bsize, uint64_t *dfree, uint64_t *dsize)`. In Solaris legacy builds, `nfs_quotas`, `my_xdr_getquota_args`, and `my_xdr_getquota_rslt` query remote rquota over RPC and parse `/etc/mnttab`/quota files. In the modern path, `disk_quotas` uses `SMB_VFS_GET_QUOTA` with `SMB_USER_FS_QUOTA_TYPE`, `SMB_USER_QUOTA_TYPE`, `SMB_GROUP_FS_QUOTA_TYPE`, and `SMB_GROUP_QUOTA_TYPE`.

## Control Flow
With sysquotas, the function first checks whether user quotas are enforced. If they are, it queries the current effective uid or, when owner inheritance means new files are owned by the directory owner, the directory/file uid under root. If the user quota is not usable, it tries group quota enforcement and then either the directory gid for setgid directories or the current effective gid. Soft limits define reported size/free space unless limits are exceeded, in which case free space is zero and total size is current usage. If quotas are disabled, unsupported, or unlimited, it returns false so callers can fall back to normal disk-free calculation.

## State And Persistence
The file does not modify quota state. It reads quota records through VFS or platform RPC/ioctl calls and writes only output values. It temporarily escalates with `become_root`/`unbecome_root` for quota lookups that must inspect inherited owner/group quota records.

## Dependencies And Integration Points
`disk_quotas` is declared in `proto.h` and feeds `get_dfree_info`/disk space reporting. It depends on `files_struct->fsp_name` stat data, loadparm `inherit owner`, current effective uid/gid, VFS quota operations, and platform quota headers. The Solaris path integrates with mount-table parsing, UFS/VxFS quota files, and NFS rquota RPC.

## Risks And Test Signals
Risks include quota enforcement detection differing by filesystem, soft-vs-hard-limit interpretation, inherited owner/group quota selection, setgid directory group handling, stale stat data, root escalation around VFS calls, and legacy Solaris/NFS RPC assumptions. Tests should cover user quota enforced, user quota disabled with group fallback, unlimited quotas, exceeded block and inode limits, inherited owner directories, setgid directories, ENOSYS from VFS modules, and normal dfree fallback when `disk_quotas` returns false.
