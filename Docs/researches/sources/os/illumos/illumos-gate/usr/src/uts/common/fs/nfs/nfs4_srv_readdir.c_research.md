# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_readdir.c

Implements the NFSv4 server READDIR operation, including directory scanning, pseudo-namespace filtering, per-entry vnode lookup, referral handling, attribute encoding, buffer sizing, and STREAMS mblk response construction.

Key elements:
- Response sizing constants define the smallest legal encoded entry, the smallest READDIR reply containing one entry, and a minimum `VOP_READDIR()` buffer large enough for `"."`, `".."`, and a maximum-name illumos `dirent64`.
- `nfs4_readdir_getvp()` looks up a child name, detects referral/reparse points for non-downrev clients, traverses mounted filesystems, obtains fids, checks exports at mount roots, runs auth against a crossed export with base credentials, and returns either the entry vnode, the mounted-on stub vnode, or a new exportinfo.
- `rfs4_get_pc_encode()` precomputes pathconf-derived attributes: max file size, max link count, and max name length.
- `rfs4_get_sb_encode()` precomputes statvfs-derived attributes: space available/free/total and file counts, preserving unknown `-1` block count semantics.
- `rfs4_op_readdir()` handles the full NFSv4 READDIR operation:
  - Validates current filehandle, directory type, minimum `maxcount`, unsupported write-only attribute requests, read access, and cookie verifier.
  - Determines whether pseudo-namespace filtering is needed based on pseudo export state, unavailable security flavor, or limited access.
  - Precomputes directory-level pathconf/statvfs data when requested attributes need it.
  - Clamps `maxcount` to server transfer size, allocates the outgoing mblk with a redzone for optimistic XDR encoding, and allocates a `VOP_READDIR()` data buffer.
  - Repeatedly calls `VOP_READDIR()` under the directory read lock, skips empty and dot entries, and filters invisible pseudo-namespace entries with `nfs_visible_inode()`.
  - Converts each returned name through `nfscmd_convname()` before encoding.
  - Looks up child vnodes only when attributes are requested, preserving `RDATTR_ERROR` behavior and skipping ENOENT races.
  - Handles referral entries by restricting attributes to RFC 7530 absent-filesystem attributes and returning `NFS4ERR_MOVED` through `rdattr_error` when needed.
  - Encodes entry cookies, names, two-word attr bitmaps, variable-length attribute blobs, and final entry/eof booleans directly into the mblk.
  - Rewinds to the last fully encoded entry on no-space, retries reading when no entries were encoded and EOF has not been reached, and returns `NFS4ERR_TOOSMALL` only when no entry can fit.
- Attribute encoding is inlined for READDIR performance:
  - Mandatory/core attributes: supported_attrs, type, fh_expire_type, change, size, link/symlink support, named_attr, fsid, unique_handles, lease_time, and rdattr_error.
  - Boolean/pathconf attributes: cansettime, case_insensitive, case_preserving, chown_restricted, homogeneous, maxfilesize, maxlink, maxname, maxread, maxwrite, no_trunc.
  - File identity: filehandle generation with `makefh4()` and named-attribute flag handling, fileid, mounted_on_fileid using `dp->d_ino`.
  - Filesystem counters: files avail/free/total and space avail/free/total from cached statvfs data.
  - Referral locations: `fetch_referral()` plus XDR encoding of `fs_locations4`.
  - Vattr-backed attributes: mode, numlinks, rawdev, space_used, access/metadata/modify times.
  - Owner/group strings: uid/gid idmap conversions are cached across entries for repeated ids and owner/group attributes are removed from an entry bitmap if mapping fails.
- Cleanup releases the READDIR data buffer, any held child vnode, owner/group UTF-8 strings, and the response mblk on error. Successful mblk ownership is left in `resp->mblk`.

Dependencies:
- Vnode/VFS APIs: `VOP_LOOKUP`, `VOP_READDIR`, `VOP_ACCESS`, `VOP_GETATTR`, `VOP_FID`, `VOP_PATHCONF`, `VFS_STATVFS`, `VOP_RWLOCK`, `VOP_RWUNLOCK`, `traverse()`, mountpoint checks.
- NFS export/security helpers: `checkexport4()`, `call_checkauth4()`, `is_exported_sec()`, `client_is_downrev()`, `nfs_visible_inode()`, `fetch_referral()`, `makefh4()`, `set_fh4_flag()`.
- Encoding helpers and protocol definitions: `IXDR_PUT_*`, `xdr_inline_encode_nfs_fh4()`, `xdr_fattr4_fs_locations()`, NFSv4 attr bitmasks, `READDIR4args`, `READDIR4res`.
- Name/id conversion: `nfscmd_convname()`, `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`.
- Kernel allocation and STREAMS: `allocb`, `allocb_wait`, `freeb`, `mblk_t`, `kmem_alloc`, `kmem_free`.
- Referral/reparse handling: `vn_is_nfs_reparse()`, `NFS4ERR_MOVED`, `ABSENT_FS_ATTRS`.

Research notes:
- READDIR has a separate fast attribute encoder instead of calling the generic attribute conversion table from `nfs4_srv_attr.c`; any new attribute support may need changes in both places.
- The redzone approach assumes bounded chunks of attribute encoding between checks. Variable-length filehandles, owner/group strings, and fs_locations have explicit pre-check or XDR bounded encoding paths.
- Pseudo namespace filtering uses directory entry inode numbers before lookup for efficiency, then carries the matching `exp_visible` entry into change-attribute and export-crossing behavior.
- There is a likely copy/paste issue in the crossed-filesystem statvfs/pathconf refresh path: the code refreshes from `dvp->v_vfsp` and `cs->vp` even while handling a child `vp` on another filesystem. This should be verified before relying on per-entry VFS attributes across mountpoints.
- `vfs_different` is only assigned inside the `if (vp && ...)` condition but is later tested unconditionally; correctness depends on its value being initialized on every entry path. This is a residual risk area for future maintenance.
