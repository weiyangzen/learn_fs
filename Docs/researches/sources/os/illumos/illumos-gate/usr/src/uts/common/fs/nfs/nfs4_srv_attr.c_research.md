# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_attr.c

Implements the server-side NFSv4 attribute conversion table. It maps NFSv4 `fattr4` bits to illumos vnode, VFS, export, idmap, ACL, referral, and pathconf data for GETATTR, SETATTR, VERIFY/NVERIFY, READDIR attribute support, and supported-attribute discovery.

Key elements:
- Global supported-attribute setup: `rfs4_attr_init()` initializes compound-state context, calls every `nfs4_ntov_map[]` handler in `NFS4ATTR_SUPPORTED` mode, builds `rfs4_supported_attrs`, and derives `supported_attrs[]` variants for NFSv4.0, v4.1, and v4.2.
- Attribute dispatch: `rfs4_ntov_init()` installs handlers for attribute indexes 0 through 56, covering mandatory attributes, recommended attributes, `mounted_on_fileid`, and `suppattr_exclcreat`.
- Mandatory attributes:
  - `rfs4_fattr4_supported_attrs()` returns the minor-version-filtered supported bitmap.
  - `rfs4_fattr4_type()` maps illumos `vtype` to NFSv4 types and handles named attribute and attribute-directory filehandle flags.
  - `rfs4_fattr4_fh_expire_type()` reports persistent filehandles by default, with optional volatile-filehandle test behavior behind `VOLATILE_FH_TEST`.
  - `rfs4_fattr4_change()` uses ctime plus `nfs_visible_change()` so pseudo-namespace changes can advance the visible NFSv4 change attribute.
  - `rfs4_fattr4_size()`, link/symlink support, named attributes, fsid, unique handles, lease time, rdattr_error, and filehandle conversion provide the rest of mandatory server attribute behavior.
- ACL handling: `rfs4_fattr4_acl()` detects filesystem ACL support with `_PC_ACL_ENABLED`, falls back to ACLENT behavior where needed, converts native ACE/ACLENT forms to NFSv4 ACEs for GET/VERIFY, and converts NFSv4 ACEs back for SETATTR under a vnode write lock. `rfs4_fattr4_aclsupport()` advertises allow and deny ACE support.
- Identity attributes: `rfs4_fattr4_owner()` and `rfs4_fattr4_owner_group()` convert uid/gid to and from NFSv4 owner strings with `nfs_idmap_*` helpers, map nfsmapid service failures to NFSv4 delay/bad-owner style errors, and free allocated UTF-8 strings in FREEIT.
- Filesystem and pathconf attributes: files/free/total, space/free/available/total/used, max file size, max link count, max name length, max read/write size, chown restriction, no-truncation, homogeneous, time delta, and raw device data are sourced from `statvfs64`, `VOP_PATHCONF()`, request transport size, and `vattr_t`.
- Referral attributes: `rfs4_fattr4_fs_locations()` calls `fetch_referral()`, copies returned `fs_locations4`, updates the referral kstat, and `rfs4_free_fs_locations4()` recursively frees pathname/location allocation.
- Mounted-on fileid: `rfs4_get_mntdfileid()` untraverses VROOT or zone-root vnodes to report the mounted-on stub nodeid when required; `rfs4_fattr4_mounted_on_fileid()` caches and verifies that value in the attribute argument.
- Settable attributes: size, mode, owner, owner_group, ACL, access time set, and modify time set populate `vattr_t` or call security-attribute VOPs. Mode SETIT strips setuid/setgid for regular files on `EX_NOSUID` exports.
- Unsupported attributes deliberately return `ENOTSUP`: archive, hidden, mimetype, quota attributes, system, backup time, create time, and several non-implemented optional fields.
- `RFS4_SUPPORT_MANDATTR_ONLY` can restrict supported-attribute discovery to mandatory attributes for debug/testing builds.

Dependencies:
- NFSv4 protocol definitions and maps: `nfs4_ntov_map`, `bitmap4`, `union nfs4_attr_u`, `FATTR4_*_MASK`, `NFS4ATTR_*`, `NFS4_MAXNUM_ATTRS`.
- Vnode and VFS interfaces: `VOP_GETATTR`, `VOP_SETSECATTR`, `VOP_GETSECATTR`, `VOP_PATHCONF`, `VOP_RWLOCK`, `VOP_RWUNLOCK`, `VFS_STATVFS` consumers through caller-provided `statvfs64`.
- NFS server helpers: `rfs4_vop_getattr()`, `makefh4()`, `xdr_inline_decode_nfs_fh4()`, `nfs_fh4_copy()`, `fetch_referral()`, `nfs_visible_change()`, `rfs4_tsize()`.
- ACL/idmap conversion helpers: `vs_acet_to_ace4`, `vs_aent_to_ace4`, `vs_ace4_to_acet`, `vs_ace4_to_aent`, `ln_ace4_cmp`, `nfs_idmap_uid_str`, `nfs_idmap_gid_str`, `nfs_idmap_str_uid`, `nfs_idmap_str_gid`.
- Export and namespace state: `compound_state`, `exportinfo`, `exi_volatile_dev`, `exi_fsid`, `is_referral`, named-attribute filehandle flags, zone root traversal.

Research notes:
- The file is table-driven: each attribute handler accepts the same command enum and must implement support probing, get, set, verify, and free behavior consistently.
- Many READDIR-compatible handlers use the `rdattr_error` convention: return `-1` when prior attribute collection failed and the caller may encode `rdattr_error` instead of failing the whole operation.
- Fsid handling has special cases for referrals and volatile device filesystems; callers that compare fsid values must preserve these wire-level encodings.
- Several VERIFY paths compare unscaled internal counters against already-scaled wire values for space attributes; this is existing behavior worth checking carefully before reusing those paths for new validation.
- `fs_locations` ownership transfers are subtle: `fetch_referral()` returns a heap wrapper whose contents are copied into the attribute union, then the wrapper is freed while nested allocations are later freed by FREEIT.
