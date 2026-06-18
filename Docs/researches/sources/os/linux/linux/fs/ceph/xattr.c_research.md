# File Research: sources/os/linux/linux/fs/ceph/xattr.c

CephFS xattr implementation, including virtual `ceph.*` attributes, cached real xattrs, local dirty xattr mutation under caps, synchronous MDS xattr operations, and security-label initialization.

Major areas:
- Valid xattr prefix filtering for `security.`, `ceph.`, `trusted.`, and `user.`.
- Virtual xattrs for layouts, directory stats, recursive stats, dir pin, quotas, snap birth time, cluster fsid, client ID, caps, auth MDS, and fscrypt auth.
- Per-inode xattr rb-tree management: set/get/remove/copy/destroy.
- Lazy decode of MDS-provided xattr blob into rb-tree.
- Re-encoding dirty xattrs into preallocated Ceph buffers.
- Get/list xattr paths with MDS getattr fallback.
- Set/remove xattr paths with local cap-backed update when possible, otherwise synchronous MDS request.
- Security label helpers and ACL/security context cleanup.

Virtual xattrs:
- Directory-only table includes `ceph.dir.layout`, layout fields, dir stat fields, recursive stat fields, `ceph.dir.pin`, `ceph.quota`, quota fields, `ceph.snap.btime`, and `ceph.caps`.
- File-only table includes `ceph.file.layout`, layout fields, `ceph.snap.btime`, and `ceph.caps`.
- Common table includes `ceph.cluster_fsid`, `ceph.client_id`, `ceph.auth_mds`, and optional `ceph.fscrypt.auth`.
- Flags distinguish read-only, hidden, recursive-stat, and dir-stat attributes.

Real xattr cache:
- `__build_xattrs()` decodes `ci->i_xattrs.blob` into `ci->i_xattrs.index` only when needed and rebuilds if version changes race during allocation.
- `__ceph_build_xattrs_blob()` re-encodes dirty rb-tree entries into `prealloc_blob`, swaps it into `blob`, clears dirty, and bumps version.
- `__set_xattr()` enforces create/replace semantics for local updates, updates size counters, tracks ownership of copied names/values, and marks entries dirty.

Get/list behavior:
- `__ceph_getxattr()` handles virtual `ceph.*` xattrs first; unrecognized `ceph.*` is passed to `ceph_do_getvxattr()`.
- Non-virtual xattrs require `CEPH_CAP_XATTR_SHARED`; otherwise it fetches xattrs from MDS.
- During trace fill (`current->journal_info`), synchronous fetch/set paths return `-EBUSY` to avoid deadlock.
- `ceph_listxattr()` ensures xattr caps, builds rb-tree, and returns/copies null-terminated name list.

Set behavior:
- Snapshot inodes reject mutation with `-EROFS`.
- Read-only virtual xattrs reject with `-EOPNOTSUPP`.
- Unknown `ceph.*` xattrs go synchronously to MDS.
- For ordinary xattrs, local mutation is used only when xattr version exists, XATTR_EXCL cap is issued, and required blob size fits `m_max_xattr_size`.
- Local mutation preallocates cap flush and xattr blob outside critical sections, marks XATTR_EXCL dirty caps, updates ctime, and marks inode dirty.
- Synchronous path builds MDS `SETXATTR` or `RMXATTR` request with optional pagelist payload.

Security integration:
- `ceph_security_xattr_wanted()` detects inode security state.
- `ceph_security_xattr_deadlock()` identifies cases where security xattr fetch would deadlock during inode initialization.
- `ceph_security_init_secctx()` encodes LSM security context into a pagelist for create requests when security labels are enabled.
- `ceph_release_acl_sec_ctx()` releases ACLs, LSM context, fscrypt auth, and pagelist.
