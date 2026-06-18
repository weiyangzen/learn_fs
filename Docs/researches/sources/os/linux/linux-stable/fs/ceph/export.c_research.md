# File Research: sources/os/linux/linux-stable/fs/ceph/export.c

## Purpose

`export.c` implements CephFS `export_operations` for NFS/exportfs support. It encodes Ceph inodes into file handles and resolves file handles, parents, and names back through cached inodes or MDS lookup operations, including special handling for snapped inodes and the synthetic snapdir.

## File Handle Formats

The file defines packed handle structures:
- `ceph_nfs_fh`: basic handle containing inode number.
- `ceph_nfs_confh`: connected handle containing inode and parent inode numbers.
- `ceph_nfs_snapfh`: snapped inode handle containing inode number, snapid, parent inode number, and dentry hash.

Handle sizes are expressed in `u32` units for exportfs.

## Encoding

`ceph_encode_fh()`:
- Delegates non-head inodes to `ceph_encode_snapfh()`.
- Encodes head inodes as `FILEID_INO32_GEN` with just inode number.
- Encodes connected head handles as `FILEID_INO32_GEN_PARENT` with inode and parent inode numbers.
- Returns `FILEID_INVALID` with the required size when the caller-provided buffer is too small.

`ceph_encode_snapfh()`:
- Encodes snapped inode identity and enough parent/hash data to help the MDS resolve non-directory snapped inodes.
- For snapped non-snapdir inodes, finds an alias dentry and records parent inode/hash unless parent is snapdir.
- For snapdir or no-parent cases, only directories are accepted; parent ino is set to the inode itself and hash to zero.
- Uses `FILEID_BTRFS_WITH_PARENT` as the fileid type for this Ceph-specific snapped format.

## Inode and Dentry Resolution

`__lookup_inode()`:
- Rejects reserved Ceph vino values as stale.
- Checks the local inode cache first.
- Falls back to MDS `LOOKUPINO` with inode/xattr mask.
- Rejects shutdown cached inodes.

`ceph_lookup_inode()` wraps `__lookup_inode()` and rejects unlinked inodes with `i_nlink == 0`.

`__fh_to_dentry()`:
- Looks up a head inode.
- Fetches `LINK_SHARED` caps through `ceph_do_getattr()` so link count is reliable.
- Returns `-ESTALE` if the inode has no links and is not currently opened.
- Returns `d_obtain_alias(inode)` for exportfs.

`__snapfh_to_dentry()`:
- Reconstructs a `ceph_vino` for either the snapped child or its parent.
- Checks local inode cache first.
- Falls back to MDS `LOOKUPINO`, passing snapid and parent/hash hints for snapped non-directory children.
- Converts returned head inode to a snapdir inode when resolving `CEPH_SNAPDIR`.
- Returns `-EOPNOTSUPP` if the MDS cannot resolve the requested snapped inode form.

## Parent Resolution

`__get_parent()` sends `LOOKUPPARENT`, either for a child dentry/inode or for an inode number from a connected handle.

`ceph_get_parent()` handles snapped dentries specially:
- Non-directory snapped children are rejected.
- For snapped directories, the head inode or snapdir of the head inode is used as parent.
- If the head directory has been unlinked, `d_obtain_root()` is used to avoid exportfs repeatedly walking disconnected parents.
- Head inodes use `LOOKUPPARENT`.

`ceph_fh_to_parent()`:
- Resolves snapped handles through `__snapfh_to_dentry(..., want_parent=true)`.
- Resolves connected head handles through `__get_parent()`.
- Falls back to parent inode from the handle if `LOOKUPPARENT` returns `-ENOENT`.

## Name Resolution

`ceph_get_name()` implements exportfs `.get_name()`:
- Snapped inodes delegate to `__get_snap_name()`.
- Head inodes use MDS `LOOKUPNAME` with parent locked.
- Plain directories copy the MDS-provided dentry name.
- Encrypted directories convert MDS name/alternate-name data back to a user-facing name through `ceph_fname_to_usr()`.

`__get_snap_name()`:
- Returns the configured snapdir name when child is the snapdir under its head directory.
- For snapshots under snapdir, iterates `LSSNAP` replies until the child snapid is found.
- Tracks `last_name` and `next_offset` to continue multi-request snapshot directory scans.

## Export Operations

`ceph_export_ops` wires:
- `.encode_fh = ceph_encode_fh`
- `.fh_to_dentry = ceph_fh_to_dentry`
- `.fh_to_parent = ceph_fh_to_parent`
- `.get_parent = ceph_get_parent`
- `.get_name = ceph_get_name`

## Important Dependencies

- `linux/exportfs.h`: file handle and export operation API.
- `mds_client.h`: `LOOKUPINO`, `LOOKUPPARENT`, `LOOKUPNAME`, `LSSNAP`, request execution, and readdir reply buffers.
- `crypto.h`: encrypted name decoding for exportfs name recovery.
- `dir.c`: `ceph_dentry_hash()` used when encoding snapped handles.
- `super.h`: Ceph inode/vino/snap helpers and snapdir helpers.

## Edge Cases and Risks

- File handles for snapped non-directory inodes require parent/hash hints because an inode number and snapid alone may not be enough for all MDS lookup paths.
- Exported head inodes with zero link count can still be valid if open; `__fh_to_dentry()` checks `__ceph_is_file_opened()`.
- Snapdir parent recovery intentionally uses `d_obtain_root()` for unlinked directories to prevent exportfs from walking further up a disconnected path.
- Encrypted `.get_name()` depends on the MDS alternate-name field when available and can fail if fscrypt conversion fails.
- `__get_snap_name()` may need multiple `LSSNAP` requests and must keep the last seen snapshot name for continuation.
